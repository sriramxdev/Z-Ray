import { useState } from "react";
import InputField from "../components/InputField";
import Button from "../components/Button";
import { Link } from "react-router-dom";

export default function Register() {
  const [form, setForm] = useState({
    username: "",
    name: "",
    license: "",
    phone: "",
    address: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(form);
  };

  return (
    <div className="h-screen flex">

      {/* LEFT BLUE 20% */}
      <div className="w-1/5 bg-gradient-to-b from-blue-700 to-blue-500 flex items-center justify-center">
        <h1 className="text-white text-3xl font-bold rotate-[-90deg] tracking-widest">
          MEDICAL AI
        </h1>
      </div>

      {/* RIGHT WHITE 80% */}
      <div className="w-4/5 flex items-center justify-center bg-gray-50">
        <form
          onSubmit={handleSubmit}
          className="w-[450px] bg-white p-8 rounded-2xl shadow-xl space-y-4"
        >
          <h2 className="text-3xl font-bold text-blue-600 text-center">
            Register
          </h2>

          <InputField
            name="username"
            placeholder="Username"
            value={form.username}
            onChange={handleChange}
          />

          <InputField
            name="name"
            placeholder="Full Name"
            value={form.name}
            onChange={handleChange}
          />

          <InputField
            name="license"
            placeholder="Medical License No."
            value={form.license}
            onChange={handleChange}
          />

          <InputField
            type="tel"
            name="phone"
            placeholder="Phone Number"
            value={form.phone}
            onChange={handleChange}
          />

          <textarea
            name="address"
            placeholder="Address"
            value={form.address}
            onChange={handleChange}
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <InputField
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
          />

          <Button text="Create Account" />

          <p className="text-center text-sm">
            Already have an account?{" "}
             
  <Link to="/" className="text-blue-600 hover:underline">
    Login
  </Link>
          </p>
        </form>
      </div>
    </div>
  );
}