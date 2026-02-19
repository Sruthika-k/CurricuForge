import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Loader2, BookOpen, Clock, Target, GraduationCap } from "lucide-react";
import { motion } from "framer-motion";

interface CurriculumFormProps {
  onGenerate: (data: FormData) => void;
  isLoading: boolean;
}

export interface FormData {
  subject: string;
  level: string;
  duration: string;
  goals: string;
}

const levels = ["Beginner", "Intermediate", "Advanced"];

const CurriculumForm = ({ onGenerate, isLoading }: CurriculumFormProps) => {
  const [form, setForm] = useState<FormData>({
    subject: "",
    level: "Beginner",
    duration: "",
    goals: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.subject.trim() || !form.duration.trim() || !form.goals.trim()) return;
    onGenerate(form);
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full max-w-2xl mx-auto space-y-6"
    >
      <div className="bg-card rounded-lg p-6 md:p-8 shadow-card space-y-5">
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <BookOpen className="h-4 w-4 text-secondary" />
            Subject Name
          </label>
          <input
            type="text"
            value={form.subject}
            onChange={(e) => setForm({ ...form, subject: e.target.value })}
            placeholder="e.g. Introduction to Machine Learning"
            className="w-full px-4 py-3 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-body"
            required
            maxLength={100}
          />
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <GraduationCap className="h-4 w-4 text-secondary" />
            Level
          </label>
          <div className="flex gap-3">
            {levels.map((level) => (
              <button
                key={level}
                type="button"
                onClick={() => setForm({ ...form, level })}
                className={`flex-1 py-2.5 px-4 rounded-md text-sm font-medium transition-all border ${
                  form.level === level
                    ? "bg-secondary text-secondary-foreground border-secondary shadow-sm"
                    : "bg-muted text-muted-foreground border-border hover:bg-accent/20"
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Clock className="h-4 w-4 text-secondary" />
            Duration
          </label>
          <input
            type="text"
            value={form.duration}
            onChange={(e) => setForm({ ...form, duration: e.target.value })}
            placeholder="e.g. 8 weeks, 3 months"
            className="w-full px-4 py-3 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-body"
            required
            maxLength={50}
          />
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm font-semibold text-foreground">
            <Target className="h-4 w-4 text-secondary" />
            Learning Goals
          </label>
          <textarea
            value={form.goals}
            onChange={(e) => setForm({ ...form, goals: e.target.value })}
            placeholder="Describe what students should learn by the end of this course..."
            rows={4}
            className="w-full px-4 py-3 rounded-md border border-input bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring font-body resize-none"
            required
            maxLength={500}
          />
        </div>

        <Button
          type="submit"
          variant="hero"
          size="lg"
          className="w-full text-base"
          disabled={isLoading || !form.subject.trim() || !form.duration.trim() || !form.goals.trim()}
        >
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Generating Curriculum...
            </>
          ) : (
            "Generate Curriculum"
          )}
        </Button>
      </div>
    </motion.form>
  );
};

export default CurriculumForm;
