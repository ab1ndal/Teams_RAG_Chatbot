// src/components/ProtectedRoute.tsx
import { useEffect, useState, type JSX } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/lib/supabaseClient";
import { toast } from "sonner";

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
  const [loading, setLoading] = useState(true);
  const [isAuthed, setIsAuthed] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkSession = async () => {
      const { data, error } = await supabase.auth.getSession();

      if (error || !data?.session) {
        toast.warning("Please login to access this page");
        navigate("/login", { state: { from: location.pathname } });
      } else {
        setIsAuthed(true);
      }

      setLoading(false);
    };

    checkSession();
  }, [navigate]);

  if (loading) return <div className="text-center p-4">Checking session...</div>;
  if (!isAuthed) return null;

  return children;
}
