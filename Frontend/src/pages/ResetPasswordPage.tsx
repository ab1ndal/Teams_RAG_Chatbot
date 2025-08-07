import { useState, useEffect } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useNavigate } from "react-router-dom";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

export default function ResetPasswordPage() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkSession = async () => {
      const { data, error } = await supabase.auth.getSession();
      if (!data?.session || error) {
        toast.error("Invalid or expired link. Please try again.");
        navigate("/forgot-password");
      }
    };

    checkSession();
  }, [navigate]);

  const handleReset = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setLoading(true);

    const { error } = await supabase.auth.updateUser({
      password,
    });

    setLoading(false);

    if (error) {
      toast.error("Password update failed", { description: error.message });
    } else {
      toast.success("Password updated successfully");
      navigate("/login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-100">
      <div className="w-full max-w-md bg-white shadow-xl rounded-2xl p-8 text-center space-y-6">
        <h2 className="text-2xl font-semibold text-amber-700">
          Reset Your Password
        </h2>
        <p className="text-sm text-gray-500">
          Enter your new password below
        </p>

        <form onSubmit={handleReset} className="space-y-4 text-left">
          <Input
            type="password"
            placeholder="New Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Confirm New Password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <Button
            type="submit"
            className="w-full py-2 bg-amber-600 text-white rounded hover:bg-amber-700 transition disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Updating..." : "Reset Password"}
          </Button>
        </form>

        <p className="text-sm text-gray-600 mt-2">
          Back to{" "}
          <a href="/login" className="text-amber-600 underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}
