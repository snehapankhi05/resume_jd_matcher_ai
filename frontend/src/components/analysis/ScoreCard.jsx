function ScoreCard({ title, value }) {
  return (
    <div className="bg-white rounded-xl shadow p-6 text-center">

      <h3 className="text-lg font-semibold text-gray-600">
        {title}
      </h3>

      <p className="text-5xl font-bold text-blue-600 mt-4">
        {value}
      </p>

    </div>
  );
}

export default ScoreCard;