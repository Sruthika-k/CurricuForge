import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Download, BookOpen, CheckCircle, FileText, Calendar } from "lucide-react";
import jsPDF from "jspdf";
import type { Curriculum } from "@/lib/mockCurriculum";

interface CurriculumResultProps {
  curriculum: Curriculum;
  subject: string;
}

const CurriculumResult = ({ curriculum, subject }: CurriculumResultProps) => {
  const downloadPDF = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    let y = 20;

    // Title
    doc.setFontSize(22);
    doc.setFont("helvetica", "bold");
    doc.text(curriculum.title, pageWidth / 2, y, { align: "center" });
    y += 12;

    doc.setFontSize(11);
    doc.setFont("helvetica", "normal");
    doc.text(`Level: ${curriculum.level} | Duration: ${curriculum.duration}`, pageWidth / 2, y, { align: "center" });
    y += 16;

    // Learning Outcomes
    doc.setFontSize(14);
    doc.setFont("helvetica", "bold");
    doc.text("Learning Outcomes", 14, y);
    y += 8;
    doc.setFontSize(10);
    doc.setFont("helvetica", "normal");
    curriculum.learningOutcomes.forEach((outcome) => {
      if (y > 270) { doc.addPage(); y = 20; }
      doc.text(`• ${outcome}`, 18, y);
      y += 6;
    });
    y += 8;

    // Weekly Syllabus
    curriculum.weeks.forEach((week) => {
      if (y > 240) { doc.addPage(); y = 20; }
      doc.setFontSize(13);
      doc.setFont("helvetica", "bold");
      doc.text(`Week ${week.week}: ${week.title}`, 14, y);
      y += 7;

      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      week.topics.forEach((topic) => {
        if (y > 270) { doc.addPage(); y = 20; }
        doc.text(`  • ${topic}`, 18, y);
        y += 5;
      });
      y += 3;

      doc.setFont("helvetica", "italic");
      doc.text(`Assignment: ${week.assignment}`, 18, y);
      y += 10;
      doc.setFont("helvetica", "normal");
    });

    doc.save(`${subject.replace(/\s+/g, "_")}_Curriculum.pdf`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-4xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="bg-card rounded-lg p-6 md:p-8 shadow-card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h2 className="text-2xl md:text-3xl font-heading text-foreground">{curriculum.title}</h2>
            <p className="text-muted-foreground mt-1">
              {curriculum.level} · {curriculum.duration}
            </p>
          </div>
          <Button variant="hero" onClick={downloadPDF} className="shrink-0">
            <Download className="h-4 w-4" />
            Download PDF
          </Button>
        </div>
      </div>

      {/* Learning Outcomes */}
      <div className="bg-card rounded-lg p-6 md:p-8 shadow-card">
        <h3 className="flex items-center gap-2 text-lg font-heading text-foreground mb-4">
          <CheckCircle className="h-5 w-5 text-secondary" />
          Learning Outcomes
        </h3>
        <ul className="space-y-2">
          {curriculum.learningOutcomes.map((outcome, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="flex items-start gap-3 text-foreground"
            >
              <span className="mt-1.5 h-2 w-2 rounded-full bg-secondary shrink-0" />
              {outcome}
            </motion.li>
          ))}
        </ul>
      </div>

      {/* Weekly Syllabus */}
      <div className="space-y-4">
        <h3 className="flex items-center gap-2 text-lg font-heading text-foreground">
          <Calendar className="h-5 w-5 text-secondary" />
          Weekly Syllabus
        </h3>
        {curriculum.weeks.map((week, i) => (
          <motion.div
            key={week.week}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
            className="bg-card rounded-lg p-6 shadow-card"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="flex items-center justify-center h-8 w-8 rounded-full bg-secondary text-secondary-foreground text-sm font-bold">
                {week.week}
              </span>
              <h4 className="font-semibold text-foreground">{week.title}</h4>
            </div>
            <div className="ml-11 space-y-3">
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Topics</p>
                <ul className="space-y-1">
                  {week.topics.map((topic, j) => (
                    <li key={j} className="flex items-start gap-2 text-sm text-foreground">
                      <BookOpen className="h-3.5 w-3.5 mt-0.5 text-secondary shrink-0" />
                      {topic}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Assignment</p>
                <p className="text-sm text-foreground flex items-start gap-2">
                  <FileText className="h-3.5 w-3.5 mt-0.5 text-secondary shrink-0" />
                  {week.assignment}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default CurriculumResult;
