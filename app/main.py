
from app.agent import query


def main() -> None:
    question = (
        "What is the combined average weight of a "
        "Scottish Terrier and a Border Collie?"
    )

    answer = query(question)

    print("\nFinal answer:")
    print(answer)


if __name__ == "__main__":
    main()
