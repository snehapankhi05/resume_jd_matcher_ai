function Step({ done, doneLabel, pendingLabel, pendingClass = "bg-gray-100" }) {
  return (
    <div className={`rounded-lg p-4 ${done ? "bg-green-100" : pendingClass}`}>
      <p className="text-lg font-semibold">
        {done ? doneLabel : pendingLabel}
      </p>
    </div>
  );
}

function ProgressTracker({
  resumeDone = false,
  jdDone = false,
  analysisDone = false,
}) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mt-6 mb-8">

      <div className="grid md:grid-cols-3 gap-4 text-center">

        <Step
          done={resumeDone}
          doneLabel="✅ Resume Upload"
          pendingLabel="⏳ Resume Upload"
        />

        <Step
          done={jdDone}
          doneLabel="✅ JD Upload"
          pendingLabel="⏳ JD Upload"
        />

        <Step
          done={analysisDone}
          doneLabel="✅ AI Analysis"
          pendingLabel="🤖 AI Analysis"
          pendingClass={resumeDone && jdDone ? "bg-blue-100" : "bg-gray-100"}
        />

      </div>

    </div>
  );
}

export default ProgressTracker;
