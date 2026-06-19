export default function SuggestionChips({ suggestions, onPick, disabled }) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="chips" role="group" aria-label="Suggested questions">
      {suggestions.map((text, i) => (
        <button
          key={i}
          type="button"
          className="chip"
          onClick={() => onPick(text)}
          disabled={disabled}
        >
          {text}
        </button>
      ))}
    </div>
  );
}
