import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

function CircularScore({ value }) {

  return (

    <div className="w-56 h-56 mx-auto">

      <CircularProgressbar
        value={value}
        text={`${value}%`}
        styles={buildStyles({
          pathColor: "#2563EB",
          trailColor: "#E5E7EB",
          textColor: "#1E3A8A",
          textSize: "16px"
        })}
      />

    </div>

  );

}

export default CircularScore;