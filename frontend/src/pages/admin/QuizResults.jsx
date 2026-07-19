import React, { useState, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ChevronLeft, ChevronDown } from "lucide-react";

const QuizResults = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  let quizType = "SCQ";
  let quizName = "Self Concept";
  if (id === "2") {
    quizType = "GWBS";
    quizName = "General Well-Being";
  } else if (id === "3") {
    quizType = "TABBPS";
    quizName = "Type A/B Personality";
  } else if (id === "4") {
    quizType = "EI";
    quizName = "Emotional Intelligence";
  }

  const eiCompetencies = ["Overall", "Self Awareness", "Managing Emotions", "Motivating Oneself", "Empathy", "Social Skill"];

  const [selectedCompetency, setSelectedCompetency] = useState("Overall");
  const [showCompetencyDropdown, setShowCompetencyDropdown] = useState(false);

  const [selectedCourse, setSelectedCourse] = useState("All");
  const [selectedYear, setSelectedYear] = useState("All");

  const [students, setStudents] = useState(() => {
    // Generate different base students based on quiz type to match screenshots somewhat, or just use one mixed list
    const baseStudents = [
      { name: "Mamta Banerjee", rollNo: "IT-2k21-86", course: "BCA", year: "1st Year", scoreA: 85, scoreB: 45, score: 13 },
      { name: "Smriti Irani", rollNo: "IT-2k21-87", course: "MCA", year: "2nd Year", scoreA: 40, scoreB: 90, score: 25 },
      { name: "Indira Gandhi", rollNo: "IT-2k21-88", course: "BTech", year: "3rd Year", scoreA: 65, scoreB: 68, score: 42 },
      { name: "Droupadi Murmu", rollNo: "IT-2k21-89", course: "BCA", year: "1st Year", scoreA: 70, scoreB: 72, score: 46 },
      { name: "Shivraj S. Chouhan", rollNo: "IT-2k21-90", course: "MCA", year: "2nd Year", scoreA: 50, scoreB: 50, score: 27 },
      { name: "Nirmala Sitharaman", rollNo: "IT-2k21-91", course: "BTech", year: "4th Year", scoreA: 35, scoreB: 95, score: 17 },
      { name: "Nitin Gadkari", rollNo: "IT-2k21-92", course: "BCA", year: "3rd Year", scoreA: 92, scoreB: 38, score: 38 },
      { name: "Raju Singh", rollNo: "IT-2k21-86", course: "BCA", year: "2nd Year", scoreA: 80, scoreB: 55, score: 67 },
      { name: "Jay Shah", rollNo: "IT-2k21-86", course: "BCA", year: "3rd Year", scoreA: 51, scoreB: 81, score: 125 },
      { name: "Amit Shah", rollNo: "IT-2k21-86", course: "BTech", year: "1st Year", scoreA: 52, scoreB: 57, score: 180 },
      { name: "Narendra Modi", rollNo: "IT-2k21-86", course: "MCA", year: "2nd Year", scoreA: 52, scoreB: 54, score: 221 },
      { name: "Mohan Yadav", rollNo: "IT-2k21-86", course: "BCA", year: "1st Year", scoreA: 41, scoreB: 39, score: 100 },
      { name: "Yogi Adityanath", rollNo: "IT-2k21-86", course: "BTech", year: "4th Year", scoreA: 51, scoreB: 81, score: 40 },
      { name: "Rahul Gandhi", rollNo: "IT-2k21-86", course: "BCA", year: "3rd Year", scoreA: 80, scoreB: 55, score: 213 },
    ];

    return baseStudents.map(s => {
      let interpretation = "";
      if (quizType === "TABBPS") {
        if (s.scoreA > 75) interpretation = "Type A";
        else if (s.scoreB > 75) interpretation = "Type B";
        else if (s.scoreA >= 50 && s.scoreB >= 50) interpretation = "Balanced";
        else interpretation = "No strong pattern";
      } else if (quizType === "GWBS") {
        if (s.score > 40) interpretation = "High";
        else if (s.score > 20) interpretation = "Average";
        else interpretation = "Low";
      } else if (quizType === "SCQ") {
        if (s.score > 200) interpretation = "High";
        else if (s.score > 150) interpretation = "Above Average";
        else if (s.score > 90) interpretation = "Average";
        else if (s.score > 50) interpretation = "Below Average";
        else interpretation = "Low";
      } else { // EI
        if (s.score > 35) interpretation = "Strength";
        else if (s.score > 20) interpretation = "Needs Attention";
        else interpretation = "Development Priority";
      }
      return { ...s, interpretation };
    });
  });

  const getInterpretationBadge = (level) => {
    switch (level) {
      case "Development Priority":
      case "Low":
        return "bg-[#F87171] text-black border-[#F87171]"; // Red
      case "Needs Attention":
      case "Average":
        return "bg-[#FDE047] text-black border-[#FDE047]"; // Yellow
      case "Strength":
      case "Above Average":
      case "Balanced":
        return "bg-[#86E8A8] text-black border-[#86E8A8]"; // Light Green
      case "High":
        return "bg-[#3A8458] text-black border-[#3A8458]"; // Dark Green
      case "Type A":
        return "bg-[#F9A8D4] text-black border-[#F9A8D4]"; // Pink
      case "Type B":
        return "bg-[#93C5FD] text-black border-[#93C5FD]"; // Light Blue
      case "No strong pattern":
        return "bg-[#D6C1B9] text-black border-[#D6C1B9]"; // Brown/Grey
      case "Below Average":
        return "bg-[#F3D8C7] text-black border-[#F3D8C7]"; // Peach/Tan
      default:
        return "bg-gray-200 text-black border-gray-200";
    }
  };

  const filteredStudents = useMemo(() => {
    return students.filter(s => {
      if (selectedCourse !== "All" && s.course !== selectedCourse) return false;
      if (selectedYear !== "All" && s.year !== selectedYear) return false;
      return true;
    });
  }, [students, selectedCourse, selectedYear]);

  const courses = ["All", "BCA", "MCA", "BTech"];
  const years = ["All", "1st Year", "2nd Year", "3rd Year", "4th Year"];

  const displayStudents = useMemo(() => {
    if (quizType !== "EI" || selectedCompetency === "Overall") return filteredStudents;
    return filteredStudents.map(s => {
      const randScore = Math.floor(Math.random() * 40) + 10;
      let interpretation = "";
      if (randScore > 35) interpretation = "Strength";
      else if (randScore > 20) interpretation = "Needs Attention";
      else interpretation = "Development Priority";
      return { ...s, score: randScore, interpretation };
    });
  }, [filteredStudents, selectedCompetency, quizType]);

  return (
    <div className="w-full h-full flex flex-col font-sans relative">
      <div className="mb-6">
        <button
          onClick={() => navigate("/admin/quizzes")}
          className="flex items-center text-[#5B5B5B] font-semibold text-sm hover:text-black mb-4 transition-colors cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          Manage Quizzes
        </button>

        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-[#386641] font-serif leading-none mb-2">
              Quiz Results
            </h1>
            <p className="text-sm text-[#9DB1A3] font-semibold">
              {quizName} • Stress Management Workshop • 6 June 2026 • 2:00 PM
            </p>
          </div>

          <div className="flex gap-4 items-center">
            <div className="flex gap-2">
              <select 
                value={selectedCourse} 
                onChange={e => setSelectedCourse(e.target.value)}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm font-semibold outline-none focus:ring-2 focus:ring-[#386641]/50 text-gray-700 cursor-pointer"
              >
                {courses.map(c => <option key={c} value={c}>{c === "All" ? "All Courses" : c}</option>)}
              </select>
              
              <select 
                value={selectedYear} 
                onChange={e => setSelectedYear(e.target.value)}
                className="bg-white border border-gray-200 rounded-lg px-3 py-2 text-sm font-semibold outline-none focus:ring-2 focus:ring-[#386641]/50 text-gray-700 cursor-pointer"
              >
                {years.map(y => <option key={y} value={y}>{y === "All" ? "All Years" : y}</option>)}
              </select>
            </div>

            {quizType === "EI" && (
              <div className="relative">
                <button 
                  onClick={() => setShowCompetencyDropdown(!showCompetencyDropdown)}
                  className="flex items-center gap-2 bg-[#2E7D4F] hover:bg-[#256641] text-white px-5 py-2.5 rounded-xl text-sm font-semibold transition-colors cursor-pointer shadow-sm"
                >
                  {selectedCompetency === "Overall" ? "Select Competency" : selectedCompetency}
                  <ChevronDown className="w-4 h-4" />
                </button>
                {showCompetencyDropdown && (
                  <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-100 shadow-xl rounded-xl z-20 overflow-hidden py-1">
                    {eiCompetencies.map(comp => (
                      <button
                        key={comp}
                        onClick={() => {
                          setSelectedCompetency(comp);
                          setShowCompetencyDropdown(false);
                        }}
                        className={`block w-full text-left px-4 py-2.5 text-sm transition-colors cursor-pointer ${selectedCompetency === comp ? 'bg-[#386641]/10 text-[#386641] font-bold' : 'text-gray-700 hover:bg-gray-50'}`}
                      >
                        {comp}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-[#F3F2F2] rounded-3xl p-8 flex-1 overflow-hidden flex flex-col">
        {quizType === "TABBPS" ? (
          <>
            <div className="grid grid-cols-7 gap-4 px-6 pb-4 border-b border-black/10 font-serif font-semibold text-black shrink-0">
              <div className="col-span-2">Student Name</div>
              <div className="text-center">Roll No.</div>
              <div className="text-center">Course & Year</div>
              <div className="text-center">Score A</div>
              <div className="text-center">Score B</div>
              <div className="text-center">Interpretation</div>
            </div>

            <div className="flex flex-col gap-4 mt-6 overflow-y-auto pr-2 pb-10 flex-1">
              {displayStudents.length === 0 ? (
                <div className="text-center py-10 text-gray-500 font-medium">No students found matching the selected filters.</div>
              ) : (
                displayStudents.map((student, idx) => (
                  <div
                    key={idx}
                    className="grid grid-cols-7 gap-4 items-center bg-[#E5E5E5] border border-transparent rounded-xl px-6 py-3 transition-colors"
                  >
                    <div className="col-span-2 text-black font-serif text-lg">
                      {student.name}
                    </div>
                    <div className="text-center text-black font-sans text-base">
                      {student.rollNo}
                    </div>
                    <div className="text-center text-black font-sans text-base flex flex-col">
                      <span>{student.course}</span>
                      <span className="text-xs text-gray-500">{student.year}</span>
                    </div>
                    <div className="text-center text-black font-sans text-base">
                      {student.scoreA}
                    </div>
                    <div className="text-center text-black font-sans text-base">
                      {student.scoreB}
                    </div>
                    <div className="flex justify-center">
                      <span
                        className={`px-6 py-1.5 rounded-full text-sm font-semibold min-w-[200px] text-center shadow-sm border ${getInterpretationBadge(
                          student.interpretation
                        )}`}
                      >
                        {student.interpretation}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        ) : (
          <>
            <div className="grid grid-cols-6 gap-4 px-6 pb-4 border-b border-black/10 font-serif font-semibold text-black shrink-0">
              <div className="col-span-2">Student Name</div>
              <div className="text-center">Roll No.</div>
              <div className="text-center">Course & Year</div>
              <div className="text-center">Score</div>
              <div className="text-center">Interpretation</div>
            </div>

            <div className="flex flex-col gap-4 mt-6 overflow-y-auto pr-2 pb-10 flex-1">
              {displayStudents.length === 0 ? (
                <div className="text-center py-10 text-gray-500 font-medium">No students found matching the selected filters.</div>
              ) : (
                displayStudents.map((student, idx) => (
                  <div
                    key={idx}
                    className="grid grid-cols-6 gap-4 items-center bg-[#E5E5E5] border border-transparent rounded-xl px-6 py-3 transition-colors"
                  >
                    <div className="col-span-2 text-black font-serif text-lg">
                      {student.name}
                    </div>
                    <div className="text-center text-black font-sans text-base">
                      {student.rollNo}
                    </div>
                    <div className="text-center text-black font-sans text-base flex flex-col">
                      <span>{student.course}</span>
                      <span className="text-xs text-gray-500">{student.year}</span>
                    </div>
                    <div className="text-center text-black font-sans text-base">
                      {student.score}
                    </div>
                    <div className="flex justify-center">
                      <span
                        className={`px-6 py-2 rounded-full text-sm font-semibold min-w-[200px] text-center shadow-sm border ${getInterpretationBadge(
                          student.interpretation
                        )}`}
                      >
                        {student.interpretation}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default QuizResults;
