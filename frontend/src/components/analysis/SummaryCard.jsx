function SummaryCard({ title, items }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6">

      <h2 className="text-xl font-bold mb-4">
        {title}
      </h2>

      <ul className="space-y-3">

        {items.map((item, index) => (
          <li
            key={index}
            className="text-gray-700"
          >
            • {item}
          </li>
        ))}

      </ul>

    </div>
  );
}

export default SummaryCard;