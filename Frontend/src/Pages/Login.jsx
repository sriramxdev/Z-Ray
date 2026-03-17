import { loginUser } from "../Services/authService"
import { useState } from "react";
import { useNavigate } from "react-router-dom";

function Login() {

const [email,setEmail] = useState("")
const [password,setPassword] = useState("")

const navigate = useNavigate()

const handleLogin = (e)=>{
e.preventDefault()

if(email==="doctor@test.com" && password==="123456"){
localStorage.setItem("token","testtoken")
navigate("/dashboard")
}else{
alert("Invalid Login")
}

}

return(

<div className="min-h-screen flex items-center justify-center bg-gradient-to-r from-blue-800 to-blue-400">

<div className="flex bg-white rounded-3xl shadow-2xl overflow-hidden w-[900px]">

{/* LEFT SIDE */}

<div className="w-1/2 bg-blue-100 flex items-center justify-center p-10">

<img
src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png"
className="w-72"
/>

</div>


{/* RIGHT SIDE */}

<div className="w-1/2 p-10">

<h2 className="text-3xl font-bold text-blue-700 mb-2">
Welcome!
</h2>

<p className="text-gray-500 mb-6">
Login to your account
</p>

<form onSubmit={handleLogin} className="space-y-4">

<input
type="email"
placeholder="Email"
className="w-full p-3 border rounded-full outline-none focus:ring-2 focus:ring-blue-500"
onChange={(e)=>setEmail(e.target.value)}
/>

<input
type="password"
placeholder="Password"
className="w-full p-3 border rounded-full outline-none focus:ring-2 focus:ring-blue-500"
onChange={(e)=>setPassword(e.target.value)}
/>

<button className="w-full bg-blue-600 text-white p-3 rounded-full hover:bg-blue-700">

Login

</button>

</form>

<p className="text-sm text-gray-500 mt-6">

Don't have an account? <span className="text-blue-600 cursor-pointer">Register</span>

</p>

</div>

</div>

</div>

)

}

export default Login