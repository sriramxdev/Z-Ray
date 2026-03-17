
// import { useState } from "react";
// import InputField from "../components/InputField";
// import Button from "../components/Button";
// import { Link } from "react-router-dom";

// export default function Register() {
//   const [form, setForm] = useState({
//     username: "",
//     name: "",
//     license: "",
//     phone: "",
//     address: "",
//     password: "",
//   });

//   const handleChange = (e) => {
//     setForm({ ...form, [e.target.name]: e.target.value });
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     console.log(form);
//   };

//   return (
//     <div className="min-h-screen flex bg-gray-50 p-6 gap-6">

//       {/* SIDEBAR */}
//       <div className="w-[260px] bg-blue-50 rounded-3xl p-5 shadow-md flex flex-col gap-5">

//         <h1 className="text-blue-700 text-xl font-bold mb-2">
//           MEDICAL AI
//         </h1>

//         {/* CARDS */}
//         <Link to="/">
//           <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//             Login
//           </div>
//         </Link>

//         <Link to="/register">
//           <div className="p-4 rounded-2xl bg-blue-600 text-white shadow-md hover:shadow-lg hover:-translate-y-1 transition cursor-pointer">
//             New Register
//           </div>
//         </Link>

//         <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//           About
//         </div>

//         <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//           Documentation
//         </div>

//       </div>

//       {/* RIGHT CONTENT */}
//       <div className="flex-1 flex items-center justify-center">

//         <form
//           onSubmit={handleSubmit}
//           className="w-[520px] bg-white p-10 rounded-3xl shadow-xl space-y-5 border"
//         >
//           <h2 className="text-3xl font-bold text-blue-600 text-center">
//             New Registration
//           </h2>

//           <InputField
//             name="username"
//             placeholder="Username"
//             value={form.username}
//             onChange={handleChange}
//           />

//           <InputField
//             name="name"
//             placeholder="Full Name"
//             value={form.name}
//             onChange={handleChange}
//           />

//           <InputField
//             name="license"
//             placeholder="Medical License No."
//             value={form.license}
//             onChange={handleChange}
//           />

//           <InputField
//             type="tel"
//             name="phone"
//             placeholder="Phone Number"
//             value={form.phone}
//             onChange={handleChange}
//           />

//           <textarea
//             name="address"
//             placeholder="Address"
//             value={form.address}
//             onChange={handleChange}
//             className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
//           />

//           <InputField
//             type="password"
//             name="password"
//             placeholder="Password"
//             value={form.password}
//             onChange={handleChange}
//           />

//           <Button text="Create Account" />

//           <p className="text-center text-sm text-gray-500">
//             Already have an account?{" "}
//             <Link to="/" className="text-blue-600 hover:underline">
//               Login
//             </Link>
//           </p>
//         </form>

//       </div>
//     </div>
//   );
// }

// import { useState } from "react";
// import InputField from "../components/InputField";
// import Button from "../components/Button";
// import { Link } from "react-router-dom";

// export default function Register() {
//   const [form, setForm] = useState({
//     username: "",
//     name: "",
//     license: "",
//     phone: "",
//     address: "",
//     password: "",
//   });

//   const handleChange = (e) => {
//     setForm({ ...form, [e.target.name]: e.target.value });
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     console.log(form);
//   };

//   return (
//     <div className="min-h-screen flex bg-white p-6 gap-6 relative overflow-hidden">

//       {/* 🔵 MEDICAL BACKGROUND ELEMENTS */}
//       <div className="absolute inset-0 z-0">

//         {/* heartbeat line */}
//         <div className="absolute top-20 left-1/3 text-blue-200 text-6xl opacity-20 animate-pulse">
//           ❤️
//         </div>

//         {/* plus icons */}
//         <div className="absolute top-10 right-20 text-blue-300 text-5xl opacity-20">+</div>
//         <div className="absolute bottom-20 left-1/3 text-blue-300 text-5xl opacity-20">+</div>

//         {/* shield */}
//         <div className="absolute bottom-10 left-10 opacity-10">
//           <img
//             src="https://cdn-icons-png.flaticon.com/512/2966/2966483.png"
//             className="w-40"
//           />
//         </div>

//         {/* DNA */}
//         <div className="absolute right-10 bottom-10 opacity-10">
//           <img
//             src="https://cdn-icons-png.flaticon.com/512/2785/2785819.png"
//             className="w-40"
//           />
//         </div>
//       </div>

//       {/* SIDEBAR */}
//       <div className="w-[260px] bg-blue-50 rounded-3xl p-5 shadow-md flex flex-col gap-5 z-10">

//         <h1 className="text-blue-700 text-xl font-bold mb-2">
//           MEDICAL AI
//         </h1>

//         <Link to="/">
//           <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//             Login
//           </div>
//         </Link>

//         <Link to="/register">
//           <div className="p-4 rounded-2xl bg-blue-600 text-white shadow-md hover:shadow-lg hover:-translate-y-1 transition cursor-pointer">
//             New Register
//           </div>
//         </Link>

//         <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//           About
//         </div>

//         <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
//           Documentation
//         </div>
//       </div>

//       {/* RIGHT CONTENT */}
//       <div className="flex-1 flex items-center justify-center z-10">

//         <form
//           onSubmit={handleSubmit}
//           className="w-[520px] bg-white/90 backdrop-blur-lg p-10 rounded-3xl shadow-xl space-y-5 border border-gray-200"
//         >
//           <h2 className="text-3xl font-bold text-blue-600 text-center">
//             New Registration
//           </h2>

//           <InputField
//             name="username"
//             placeholder="Username"
//             value={form.username}
//             onChange={handleChange}
//           />

//           <InputField
//             name="name"
//             placeholder="Full Name"
//             value={form.name}
//             onChange={handleChange}
//           />

//           <InputField
//             name="license"
//             placeholder="Medical License No."
//             value={form.license}
//             onChange={handleChange}
//           />

//           <InputField
//             type="tel"
//             name="phone"
//             placeholder="Phone Number"
//             value={form.phone}
//             onChange={handleChange}
//           />

//           <textarea
//             name="address"
//             placeholder="Address"
//             value={form.address}
//             onChange={handleChange}
//             className="w-full p-3 rounded-xl border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
//           />

//           <InputField
//             type="password"
//             name="password"
//             placeholder="Password"
//             value={form.password}
//             onChange={handleChange}
//           />

//           <Button text="Create Account" />

//           <p className="text-center text-sm text-gray-500">
//             Already have an account?{" "}
//             <Link to="/" className="text-blue-600 hover:underline">
//               Login
//             </Link>
//           </p>
//         </form>
//       </div>
//     </div>
//   );
// }

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

        <Link to="/">
          <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
            Login
          </div>
        </Link>

        <Link to="/register">
          <div className="p-4 rounded-2xl bg-blue-600 text-white shadow-md hover:shadow-lg hover:-translate-y-1 transition cursor-pointer">
            New Register
          </div>
        </Link>

        <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
          About
        </div>

        <div className="p-4 rounded-2xl bg-white shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer">
          Documentation
        </div>
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