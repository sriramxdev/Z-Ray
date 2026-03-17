// import { loginUser } from "../Services/authService";
// import { useState } from "react";
// import { useNavigate, Link } from "react-router-dom"; 

// function Login() {

//   const [email,setEmail] = useState("")
//   const [password,setPassword] = useState("")

//   const navigate = useNavigate()

//   const handleLogin = (e)=>{
//     e.preventDefault()

//     if(email==="doctor@test.com" && password==="123456"){
//       localStorage.setItem("token","testtoken")
//       navigate("/dashboard")
//     }else{
//       alert("Invalid Login")
//     }
//   }

//   return(

//     <div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-800 to-blue-400">

//       <div className="flex bg-white rounded-3xl shadow-2xl overflow-hidden w-[900px]">

//         {/* LEFT SIDE */}
//         <div className="w-1/2 bg-blue-100 flex items-center justify-center p-10">
//           <img
//             src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
//             className="w-72"
//           />
//         </div>

//         {/* RIGHT SIDE */}
//         <div className="w-1/2 p-10">

//           <h2 className="text-3xl font-bold text-blue-700 mb-2">
//             Welcome!
//           </h2>

//           <p className="text-gray-500 mb-6">
//             Login to your account
//           </p>

//           <form onSubmit={handleLogin} className="space-y-4">

//             <input
//               type="email"
//               placeholder="Email"
//               className="w-full p-3 border rounded-full outline-none focus:ring-2 focus:ring-blue-500"
//               onChange={(e)=>setEmail(e.target.value)}
//             />

//             <input
//               type="password"
//               placeholder="Password"
//               className="w-full p-3 border rounded-full outline-none focus:ring-2 focus:ring-blue-500"
//               onChange={(e)=>setPassword(e.target.value)}
//             />

//             <button className="w-full bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700">
//               Login
//             </button>

//           </form>

//           {/* ✅ FIX HERE */}
//           <p className="text-sm text-gray-500 mt-6">
//             Don't have an account?{" "}
            
//             <Link 
//               to="/register" 
//               className="text-blue-600 hover:underline font-medium"
//             >
//               Register
//             </Link>

//           </p>

//         </div>

//       </div>

//     </div>

//   )

// }

// export default Login

import { loginUser } from "../Services/authService";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    if (email === "doctor@test.com" && password === "123456") {
      localStorage.setItem("token", "testtoken");
      navigate("/dashboard");
    } else {
      alert("Invalid Login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">

      {/* MAIN CARD */}
      <div className="flex w-[1000px] rounded-3xl shadow-xl overflow-hidden border">

        {/* LEFT SIDE (Light Medical UI) */}
        <div className="w-1/2 bg-blue-50 flex flex-col items-center justify-center p-10 relative">

          {/* subtle icons background */}
          <div className="absolute opacity-10 text-blue-300 text-9xl top-10 left-10">+</div>
          <div className="absolute opacity-10 text-blue-300 text-7xl bottom-10 right-10">❤</div>

          <img
            src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
            className="w-64 mb-6"
          />

          <h2 className="text-xl font-semibold text-blue-700">
            AI Medical System
          </h2>

          <p className="text-gray-500 text-sm text-center mt-2">
            Smart healthcare solutions for better diagnosis
          </p>
        </div>

        {/* RIGHT SIDE (75% WHITE UI) */}
        <div className="w-1/2 p-12 bg-white">

          <h2 className="text-3xl font-bold text-blue-700 mb-2">
            Welcome Back 👋
          </h2>

          <p className="text-gray-500 mb-8">
            Login to continue to your dashboard
          </p>

          <form onSubmit={handleLogin} className="space-y-5">

            {/* Email */}
            <div>
              <label className="text-sm text-gray-600">Email</label>
              <input
                type="email"
                placeholder="Enter your email"
                className="w-full mt-1 p-3 border rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password */}
            <div>
              <label className="text-sm text-gray-600">Password</label>
              <input
                type="password"
                placeholder="Enter your password"
                className="w-full mt-1 p-3 border rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {/* Forgot */}
            <div className="text-right">
              <span className="text-sm text-blue-600 cursor-pointer hover:underline">
                Forgot Password?
              </span>
            </div>

            {/* Button */}
            <button className="w-full bg-blue-600 text-white p-3 rounded-xl hover:bg-blue-700 transition">
              Login
            </button>

          </form>

          {/* Register */}
          <p className="text-sm text-gray-500 mt-8 text-center">
            Don't have an account?{" "}
            <Link
              to="/register"
              className="text-blue-600 hover:underline font-medium"
            >
              Register
            </Link>
          </p>

        </div>
      </div>
    </div>
  );
}

export default Login;