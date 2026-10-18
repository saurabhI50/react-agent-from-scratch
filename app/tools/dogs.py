
DOG_WEIGHTS = {
    "scottish terrier": 22,
    "border collie": 37,
    "toy poodle": 6,
}


def average_dog_weight(name: str) -> str:
    """Return the average weight for a supported dog breed."""

    breed = name.strip().lower()

    if breed in DOG_WEIGHTS:
        return f"{name.strip()} weighs an average of {DOG_WEIGHTS[breed]} lbs."

    supported = ", ".join(DOG_WEIGHTS.keys())
    return (
        f"Unknown breed: {name.strip()}. "
        f"Supported breeds: {supported}."
    )