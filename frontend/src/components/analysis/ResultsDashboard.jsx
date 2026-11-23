import ScoreCard from "./ScoreCard";
import SkillsList from "./SkillsList";
import SummaryCard from "./SummaryCard";
import CircularScore from "./CircularScore";

function ResultsDashboard({ results }) {

  if (!results) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-10 mt-10 text-center">

        <h2 className="text-2xl font-bold text-gray-600">
          Upload Resume and JD to start analysis
        </h2>

      </div>
    );
  }

  // When the JD contains none of the known skills, a technical score of
  // 0% would be misleading, so it is shown as N/A.
  const hasJdSkills = (results.jd_skills || []).length > 0;

  return (
    <div className="mt-10 space-y-8">

      {results.domain_match === false && (
        <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 rounded-xl p-4 font-medium">
          ⚠️ The resume and the job description appear to belong to different domains.
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">

        <div className="bg-white rounded-xl shadow-lg p-8">

          <h2 className="text-3xl font-bold text-center mb-8">
            Overall Match
          </h2>

          <CircularScore
            value={Math.round(results.overall_score)}
          />

        </div>

        <ScoreCard
          title="Technical Score"
          value={hasJdSkills ? `${results.technical_score}%` : "N/A"}
        />

        <ScoreCard
          title="Semantic Score"
          value={`${results.semantic_similarity}%`}
        />

      </div>

      <div className="grid md:grid-cols-2 gap-6">

        <SkillsList
          title="Matched Skills"
          skills={results.matched_skills}
          color="green"
        />

        <SkillsList
          title="Missing Skills"
          skills={results.missing_skills}
          color="red"
        />

      </div>

      <SummaryCard
        title="Strengths"
        items={results.strengths}
      />

      <SummaryCard
        title="Weaknesses"
        items={results.weaknesses}
      />

      <SummaryCard
        title="Suggestions"
        items={results.suggestions}
      />

      <div className="bg-white rounded-xl shadow p-6">

        <h2 className="text-xl font-bold mb-3">
          Summary
        </h2>

        <p className="text-gray-700">
          {results.summary}
        </p>

      </div>

    </div>
  );
}

export default ResultsDashboard;
