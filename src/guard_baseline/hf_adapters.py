from __future__ import annotations

from typing import Any

from guard_baseline.adapters import TargetAdapter
from guard_baseline.schema import Seed, Turn


def _torch_dtype(dtype_name: str) -> Any:
    import torch

    mapping = {
        "auto": "auto",
        "float16": torch.float16,
        "fp16": torch.float16,
        "bfloat16": torch.bfloat16,
        "bf16": torch.bfloat16,
        "float32": torch.float32,
        "fp32": torch.float32,
    }
    if dtype_name not in mapping:
        raise ValueError(f"Unsupported torch_dtype: {dtype_name}")
    return mapping[dtype_name]


class TransformersTargetModel(TargetAdapter):
    """Local Hugging Face causal LM target adapter.

    This adapter is intentionally generic. It is suitable for smoke tests with
    Llama/Qwen/Gemma/Mistral/Vicuna-style chat models, as long as their tokenizer
    exposes a chat template or can accept a plain text fallback prompt.
    """

    def __init__(self, name: str, **params: object) -> None:
        super().__init__(name, **params)
        self._tokenizer = None
        self._model = None

    def _load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return

        from transformers import AutoModelForCausalLM, AutoTokenizer

        model_path = self.params.get("model_path")
        if not model_path:
            raise ValueError(f"Target '{self.name}' requires params.model_path.")

        trust_remote_code = bool(self.params.get("trust_remote_code", True))
        dtype = _torch_dtype(str(self.params.get("torch_dtype", "auto")))
        device_map = self.params.get("device_map", "auto")

        self._tokenizer = AutoTokenizer.from_pretrained(
            str(model_path),
            trust_remote_code=trust_remote_code,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            str(model_path),
            torch_dtype=dtype,
            device_map=device_map,
            trust_remote_code=trust_remote_code,
        )
        self._model.eval()

    def generate(self, history: list[Turn], seed: Seed) -> str:
        self._load()
        assert self._tokenizer is not None
        assert self._model is not None

        messages = [{"role": turn.role, "content": turn.content} for turn in history if turn.role in {"user", "assistant"}]
        if getattr(self._tokenizer, "chat_template", None):
            prompt = self._tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        else:
            prompt = self._plain_prompt(messages)

        inputs = self._tokenizer(prompt, return_tensors="pt")
        inputs = {key: value.to(self._model.device) for key, value in inputs.items()}

        max_new_tokens = int(self.params.get("max_new_tokens", 256))
        temperature = float(self.params.get("temperature", 0.0))
        do_sample = temperature > 0.0
        generation_kwargs: dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self._tokenizer.eos_token_id,
        }
        if do_sample:
            generation_kwargs["temperature"] = temperature

        output_ids = self._model.generate(**inputs, **generation_kwargs)
        new_tokens = output_ids[0][inputs["input_ids"].shape[-1] :]
        return self._tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    @staticmethod
    def _plain_prompt(messages: list[dict[str, str]]) -> str:
        rendered = []
        for message in messages:
            rendered.append(f"{message['role'].upper()}: {message['content']}")
        rendered.append("ASSISTANT:")
        return "\n".join(rendered)
