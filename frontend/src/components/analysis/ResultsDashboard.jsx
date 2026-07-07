import ScoreCard from "./ScoreCard";
import SkillsList from "./SkillsList";
import SummaryCard from "./SummaryCard";

function ResultsDashboard({ results }) {
  if (!results) return null;

  return (
    <div className="mt-10 space-y-8">

      <div className="grid md:grid-cols-3 gap-6">

        <ScoreCard
          title="Overall Match"
          value={`${results.overall_score}%`}
        />

        <ScoreCard
          title="Technical Score"
          value={`${results.technical_score}%`}
        />

        <ScoreCard
          title="Semantic Score"
          value={`${Math.round(results.semantic_similarity * 100)}%`}
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