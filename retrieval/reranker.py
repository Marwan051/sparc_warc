import os
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True) 
class RerankerConfig:
    model_dir: Path
    max_length: int = 512
    batch_size: int = 4
    intra_op_threads: int = 1

    @classmethod
    def from_environment(cls) -> "RerankerConfig":
        model_dir = Path(
        os.environ.get(
            "RERANKER_MODEL_DIR",
            ".models/bge-reranker-v2-m3-int8",
        )
    ).expanduser().resolve()

        max_length = _positive_int("RERANKER_MAX_LENGTH",512)
        batch_size = _positive_int("RERANKER_BATCH_SIZE",4)
        intra_op_threads = _positive_int("RERANKER_INTRA_OP_THREADS",1)

        return cls(
        model_dir=model_dir,
        max_length=max_length,
        batch_size=batch_size,
        intra_op_threads=intra_op_threads,
    )       


def _positive_int(name: str, default: int) -> int:
    raw = os.environ.get(name, str(default))

    try:
        value = int(raw)
    except ValueError as error:
        raise ValueError(
            f"{name} must be an integer, got {raw!r}"
        ) from error

    if value < 1:
        raise ValueError(f"{name} must be at least 1, got {value}")

    return value


def sigmoid(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)

    if not np.all(np.isfinite(values)):
        raise ValueError("reranker logits contain non-finite values")

    result = np.empty_like(values)
    positive = values >= 0

    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))

    exp_values = np.exp(values[~positive])
    result[~positive] = exp_values / (1.0 + exp_values)

    return result.astype(np.float32)

def validate_logits(logits:np.ndarray,expected_count:int) ->np.ndarray:
    values = np.asarray(logits,dtype=np.float32)
    if values.ndim == 2 and values.shape[1] == 1:
        values = values[:,0]

    if values.ndim != 1:
        raise ValueError(
        f"reranker output must contain one score per pair, got shape {values.shape}"
    )
    if len(values) != expected_count:
        raise ValueError(
        f"reranker returned {len(values)} scores "
        f"for {expected_count} input pairs"
    )

    
    if not np.all(np.isfinite(values)):
        raise ValueError("reranker returned a non-finite score")
    return values


class OnnxReranker:
    def __init__(self, config: RerankerConfig | None = None):
        self.config :RerankerConfig =config or RerankerConfig.from_environment()
        self._tokenizer= None
        self._session = None 
        self._input_names: set[str] = set()
        self._output_name: str | None = None
        self._load_lock =threading.Lock()
        self._inference_lock = threading.Lock()


    def ensure_loaded(self) -> None:
        if self._session is not None:
            return
        
        with self._load_lock:
            if self._session is not None:
                return
            
            import onnxruntime as ort
            from transformers import AutoTokenizer

            model_path = self.config.model_dir / "onnx" / "model_int8.onnx"
            if not model_path.is_file():
                raise FileNotFoundError(f"Missing reranker model: {model_path}")

            tokenizer = AutoTokenizer.from_pretrained(self.config.model_dir,local_files_only=True)

            options = ort.SessionOptions()
            options.intra_op_num_threads = self.config.intra_op_threads
            options.inter_op_num_threads = 1
            options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

            session = ort.InferenceSession(str(model_path),
                sess_options=options,
                providers=["CPUExecutionProvider"],
                )

            input_names = {
                item.name
                for item in session.get_inputs()
            }

            required_inputs = {
                "input_ids",
                "attention_mask",
            }

            missing_inputs = required_inputs - input_names

            if missing_inputs:
                raise RuntimeError(
                    "Reranker model is missing required inputs: "
                    f"{sorted(missing_inputs)}"
                )

            outputs = session.get_outputs()

            if len(outputs) != 1:
                raise RuntimeError(
                    "Expected exactly one reranker output, "
                    f"found {len(outputs)}"
                )

            output_name = outputs[0].name

            self._tokenizer = tokenizer
            self._input_names = input_names
            self._output_name = output_name

            self._session = session


    def score(self, pairs: list[tuple[str, str]]) -> np.ndarray:
        if not pairs:
            return np.empty(0,dtype=np.float32)
        for pair in pairs:
            if (
                not isinstance(pair, tuple)
                or len(pair) != 2
                or not all(isinstance(value, str) for value in pair)
                ):
                raise TypeError(
                    "each reranker pair must be a (query, passage) tuple of strings"
                )        
        batches = []
        for start in range(0, len(pairs), self.config.batch_size):
            batch = pairs[start:start + self.config.batch_size]
            batches.append(self._run_batch(batch))

        logits = np.concatenate(batches)
        logits = validate_logits(logits, len(pairs))
        return sigmoid(logits) 

    def _tokenize(self, pairs: list[tuple[str, str]]) -> dict[str, np.ndarray]:
        queries = [query for query,_ in pairs]
        passages = [passage for _,passage in pairs]
        if self._tokenizer is None:
            raise RuntimeError("Reranker tokenizer was not initialized")
        tokens = self._tokenizer(queries,passages,padding=True,truncation=True,max_length=self.config.max_length,return_tensors="np")
        missing = self._input_names.difference(tokens)
        if missing:
            raise RuntimeError(
                "Tokenizer did not produce required reranker inputs: "
                f"{sorted(missing)}"
            )

        return {
            name: np.asarray(tokens[name])
            for name in self._input_names
        } 
    

    def _run_batch(self, pairs: list[tuple[str, str]]) -> np.ndarray:
        if not pairs:
            return np.empty(0,dtype=np.float32)

        self.ensure_loaded()

        if self._session is None or self._output_name is None:
            raise RuntimeError("Reranker was not initialized correctly")
        assert self._tokenizer is not None
        inputs= self._tokenize(pairs)

        with self._inference_lock:
            outputs = self._session.run([self._output_name],inputs)
            if len(outputs) != 1:
                raise RuntimeError(
                    f"Expected one reranker output, received {len(outputs)}"
                    )

            raw_logits = outputs[0]
            if not isinstance(raw_logits, np.ndarray):
                raise TypeError(
                    "Expected dense reranker logits, "
                    f"received {type(raw_logits).__name__}"
                    )
    
        return validate_logits(raw_logits, len(pairs))
            



