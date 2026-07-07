from dotenv import load_dotenv
import os
from db_init import init_database
from src.evaluation.generator import EvaluationGenerator
from src.llm.openai_llm import OpenAILLM


def main():
    load_dotenv()
    _, chunks = init_database()

    llm = OpenAILLM(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model=os.getenv("OPENAI_MODEL"),
    )

    generator = EvaluationGenerator(llm)
    samples = generator.generate_from_chunks(
        chunks,
        questions_per_chunk=3,
        limit=30,
    )
    generator.save(samples, "src/evaluation/generated_dataset.json")
    print(f"Generated {len(samples)} evaluation samples.")


if __name__ == "__main__":
    main()