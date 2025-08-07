import { useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function SignupPage() {
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [department, setDepartment] = useState("");
  const [title, setTitle] = useState("");

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    setLoading(true);

    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });

    if (error || !data?.user) {
      setLoading(false);
      toast.error("Signup failed", { description: error?.message });
      return;
    }

    const { id } = data.user;

    const { error: insertError } = await supabase.from("users").insert({
      id,
      first_name: firstName,
      last_name: lastName,
      email,
      department,
      title,
    });

    setLoading(false);

    if (insertError) {
      toast.error("Account created, but user info failed", {
        description: insertError.message,
      });
    } else {
      toast.success("Signup successful");
      navigate("/chat");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-100">
      <div className="w-full max-w-md bg-white shadow-xl rounded-2xl p-8 text-center space-y-6">
        <h2 className="text-2xl font-semibold text-amber-700">Create Account</h2>
        <p className="text-sm text-gray-500">
          Fill in your details to sign up for NYA Chatbot
        </p>

        <form onSubmit={handleSignup} className="space-y-4 text-left">
          <Input
            type="text"
            placeholder="First Name"
            required
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Last Name"
            required
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Department (optional)"
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Input
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Confirm Password"
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <Button
            type="submit"
            className="w-full py-2 bg-amber-600 text-white rounded hover:bg-amber-700 transition disabled:opacity-50"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Sign Up"}
          </Button>
        </form>

        <p className="text-sm text-gray-600 mt-2">
          Already have an account?{" "}
          <a href="/login" className="text-amber-600 underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
}
