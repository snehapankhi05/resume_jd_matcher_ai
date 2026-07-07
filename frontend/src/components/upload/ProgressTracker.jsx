function ProgressTracker() {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6 mb-8">

      <div className="grid md:grid-cols-3 gap-4 text-center">

        <div className="bg-green-100 rounded-lg p-4">
          <p className="text-lg font-semibold">
            ✅ Resume Upload
          </p>
        </div>

        <div className="bg-green-100 rounded-lg p-4">
          <p className="text-lg font-semibold">
            ✅ JD Upload
          </p>
        </div>

        <div className="bg-blue-100 rounded-lg p-4">
          <p className="text-lg font-semibold">
            🤖 AI Analysis
          </p>
        </div>

      </div>

    </div>
  );
}

export default ProgressTracker;