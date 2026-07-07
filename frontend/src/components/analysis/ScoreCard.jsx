function ScoreCard({ title, value }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg h-48 flex flex-col justify-center items-center hover:shadow-2xl hover:-translate-y-2 transition-all duration-300">

      <h3 className="text-gray-500 text-lg font-semibold">
        {title}
      </h3>

      <h1 className="mt-3 text-5xl font-bold text-blue-600">
        {value}
      </h1>

    </div>
  );
}

export default ScoreCard;