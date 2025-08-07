import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const redirectTo = location.state?.from || "/chat";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);

    if (error) {
      toast.error("Login failed", { description: error.message });
    } else {
      toast.success("Login successful");
      navigate(redirectTo);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-100">
      <div className="w-full max-w-md bg-white shadow-xl rounded-2xl p-8 text-center space-y-6">
        <h2 className="text-2xl font-semibold text-amber-700">
          NYA Chatbot Login
        </h2>
        <p className="text-sm text-gray-500">
          Use your email and password to sign in
        </p>

        <form onSubmit={handleLogin} className="space-y-4 text-left">
            <Input
                type="email"
                placeholder="Enter your Email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border rounded text-sm"
            />
            <Input
                type="password"
                placeholder="Password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-3 py-2 border rounded text-sm"
            />
            <Button 
                type="submit" 
                className="w-full py-2 bg-amber-600 text-white rounded hover:bg-amber-700 transition disabled:opacity-50" 
                disabled={loading}
            >
                {loading ? "Logging in..." : "Login with Email"}
            </Button>
        </form>

        <p className="text-sm text-right">
          <a href="/forgot-password" className="text-amber-600 underline">
            Forgot Password?
          </a>
        </p>

        <p className="text-sm text-gray-600 mt-2">
          Don't have an account?{" "}
          <a href="/signup" className="text-amber-600 underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  );
}
