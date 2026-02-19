import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { BookOpen, Sparkles, FileDown, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import CurriculumForm, { type FormData } from "@/components/CurriculumForm";
import CurriculumResult from "@/components/CurriculumResult";
import { generateMockCurriculum, type Curriculum } from "@/lib/mockCurriculum";
import heroBg from "@/assets/hero-bg.jpg";

const features = [
  { icon: Sparkles, title: "AI-Powered", desc: "Generate complete curricula in seconds" },
  { icon: BookOpen, title: "Structured", desc: "Weekly syllabus, topics & assignments" },
  { icon: FileDown, title: "PDF Export", desc: "Download and share your curriculum" },
  { icon: Zap, title: "Instant", desc: "No waiting — results in moments" },
];

const Index = () => {
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [subject, setSubject] = useState("");
  const resultRef = useRef<HTMLDivElement>(null);

  const handleGenerate = async (data: FormData) => {
    setIsLoading(true);
    setSubject(data.subject);
    // Simulate AI generation delay
    await new Promise((r) => setTimeout(r, 1500));
    const result = generateMockCurriculum(data.subject, data.level, data.duration, data.goals);
    setCurriculum(result);
    setIsLoading(false);
    setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
  };

  const handleReset = () => {
    setCurriculum(null);
    setSubject("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: `url(${heroBg})` }}
        />
        <div className="absolute inset-0 bg-primary/85" />
        <div className="relative z-10 px-4 py-20 md:py-32 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-6xl font-heading text-primary-foreground mb-4 leading-tight">
              CurricuForge
            </h1>
            <p className="text-lg md:text-xl text-primary-foreground/80 mb-8 font-body max-w-xl mx-auto">
              Create professional, structured curricula in seconds with the power of AI. Just enter your details and let us do the rest.
            </p>
            <div className="flex items-center justify-center gap-4">
              <Button
                variant="hero"
                size="lg"
                onClick={() => document.getElementById("generator")?.scrollIntoView({ behavior: "smooth" })}
              >
                Get Started
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
              className="bg-card rounded-lg p-5 shadow-card text-center"
            >
              <f.icon className="h-8 w-8 mx-auto mb-3 text-secondary" />
              <h3 className="font-semibold text-foreground text-sm">{f.title}</h3>
              <p className="text-muted-foreground text-xs mt-1">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Generator Section */}
      <section id="generator" className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl md:text-4xl font-heading text-foreground mb-2">
              Build Your Curriculum
            </h2>
            <p className="text-muted-foreground">
              Fill in the details below and generate a complete curriculum instantly.
            </p>
          </div>

          {!curriculum ? (
            <CurriculumForm onGenerate={handleGenerate} isLoading={isLoading} />
          ) : (
            <div ref={resultRef}>
              <CurriculumResult curriculum={curriculum} subject={subject} />
              <div className="text-center mt-8">
                <Button variant="outline" onClick={handleReset}>
                  Generate Another Curriculum
                </Button>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <p className="text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} CurricuForge — AI-Powered Curriculum Generation
        </p>
      </footer>
    </div>
  );
};

export default Index;
