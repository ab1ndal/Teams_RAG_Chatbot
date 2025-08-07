import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/reset-password`, // adjust route if needed
    });

    setLoading(false);

    if (error) {
      toast.error("Reset failed", { description: error.message });
    } else {
      toast.success("Password reset email sent", {
        description: "Check your inbox for instructions.",
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-100">
      <div className="w-full max-w-md bg-white shadow-xl rounded-2xl p-8 text-center space-y-6">
        <h2 className="text-2xl font-semibold text-amber-700">
          Forgot Password
        </h2>
        <p className="text-sm text-gray-500">
          Enter your email to receive a password reset link
        </p>

        <form onSubmit={handleResetPassword} className="space-y-4 text-left">
          <Input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <Button
            type="submit"
            className="w-full py-2 bg-amber-600 text-white rounded hover:bg-amber-700 transition disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Sending..." : "Send Reset Link"}
          </Button>
        </form>

        <p className="text-sm text-gray-600 mt-2">
          Remembered your password?{" "}
          <a href="/login" className="text-amber-600 underline">
            Go to login
          </a>
        </p>
      </div>
    </div>
  );
}
