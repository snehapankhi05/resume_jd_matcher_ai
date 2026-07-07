import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

function CircularScore({ value }) {
  return (
    <div className="w-52 h-52 mx-auto">

      <CircularProgressbar
        value={value}
        text={`${value}%`}
        styles={buildStyles({
          pathColor: "#2563eb",
          textColor: "#1e293b",
          trailColor: "#e2e8f0",
          textSize: "16px"
        })}
      />

    </div>
  );
}

export default CircularScore;