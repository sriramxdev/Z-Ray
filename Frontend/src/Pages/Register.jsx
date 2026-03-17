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
    <div className="min-h-screen flex bg-white p-6 gap-6 relative overflow-hidden">

      {/* 🔵 BACKGROUND MEDICAL IMAGE */}
      <div className="absolute inset-0 flex items-center justify-center z-0 opacity-10">
        <img
          src="https://cdn-icons-png.flaticon.com/512/4320/4320371.png"
          className="w-[900px]"
        />
      </div>

      {/* SIDEBAR */}
      <div className="w-[260px] bg-blue-50 rounded-3xl p-5 shadow-md flex flex-col gap-5 z-10">

        <h1 className="text-blue-700 text-xl font-bold mb-2">
          MEDICAL AI
        </h1>

        {/* <Link to="/">
          <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
            Login
          </div>
        </Link> */}
        <Link to="/">
  <div className="p-4 rounded-2xl bg-white text-blue-600 shadow-sm 
                  hover:bg-blue-600 hover:text-white 
                  hover:shadow-md hover:-translate-y-1 
                  transition duration-300 ease-in-out cursor-pointer">
    Login
  </div>
</Link>

        <Link to="/register">
          <div className="p-4 rounded-2xl bg-blue-600 text-white shadow-md hover:shadow-lg hover:-translate-y-1 transition cursor-pointer">
            New Register
          </div>
        </Link>

        {/* <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
          About
        </div> */}
        <Link to="/about">
  <div className="p-4 rounded-2xl bg-white shadow-sm hover:bg-blue-600 hover:text-white hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
    About
  </div>
</Link>

      </div>

      {/* RIGHT CONTENT */}
      <div className="flex-1 flex items-center justify-center z-10">

        <form
          onSubmit={handleSubmit}
          className="w-[520px] bg-white/95 backdrop-blur-xl p-10 rounded-3xl shadow-2xl space-y-5 border border-gray-200"
        >
          <h2 className="text-3xl font-bold text-blue-600 text-center">
            New Registration
          </h2>

          {/* Username */}
          <div className="flex items-center border rounded-xl px-3">
            <span className="text-gray-400">👤</span>
            <input
              name="username"
              placeholder="Username"
              value={form.username}
              onChange={handleChange}
              className="w-full p-3 outline-none"
            />
          </div>

          {/* Name */}
          <div className="flex items-center border rounded-xl px-3">
            <span className="text-gray-400">🪪</span>
            <input
              name="name"
              placeholder="Full Name"
              value={form.name}
              onChange={handleChange}
              className="w-full p-3 outline-none"
            />
          </div>

          {/* License */}
          <div className="flex items-center border rounded-xl px-3">
            <span className="text-gray-400">📄</span>
            <input
              name="license"
              placeholder="Medical License No."
              value={form.license}
              onChange={handleChange}
              className="w-full p-3 outline-none"
            />
          </div>

          {/* Phone */}
          <div className="flex items-center border rounded-xl px-3">
            <span className="text-gray-400">📞</span>
            <input
              type="tel"
              name="phone"
              placeholder="Phone Number"
              value={form.phone}
              onChange={handleChange}
              className="w-full p-3 outline-none"
            />
          </div>

          {/* Address */}
          <div className="flex items-start border rounded-xl px-3">
            <span className="text-gray-400 mt-3">📍</span>
            <textarea
              name="address"
              placeholder="Address"
              value={form.address}
              onChange={handleChange}
              className="w-full p-3 outline-none resize-none"
            />
          </div>

          {/* Password */}
          <div className="flex items-center border rounded-xl px-3">
            <span className="text-gray-400">🔒</span>
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              className="w-full p-3 outline-none"
            />
          </div>

          <button className="w-full bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition">
            Create Account
          </button>

          <p className="text-center text-sm text-gray-500">
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
