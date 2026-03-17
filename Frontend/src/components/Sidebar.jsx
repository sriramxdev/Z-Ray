
// import { useState } from "react"
// import { useNavigate } from "react-router-dom"
// import {
//   Home,
//   Upload,
//   Activity,
//   FileText,
//   BarChart,
//   Info,
//   ScanLine,
//   HeartPulse
// } from "lucide-react"

// const menu = [
//   { name: "Dashboard", icon: Home },
//   { name: "Upload Scan", icon: Upload },
//   { name: "AI Result", icon: Activity },
//   { name: "X-Ray Analysis", icon: ScanLine },
//   { name: "MRI Analysis", icon: ScanLine },
//   { name: "ECG Analysis", icon: HeartPulse },
//   { name: "History", icon: FileText },
//   { name: "Trends", icon: BarChart },
//   { name: "About", icon: Info },
// ]

// export default function Sidebar() {
//   const [active, setActive] = useState("Dashboard")
//   const navigate = useNavigate()

//   const handleLogout = () => {
//     // agar token use kar rahe ho to remove karo
//     localStorage.removeItem("token")

//     // redirect to login
//     navigate("/")
//   }

//   return (
//     <div className="w-64 h-screen bg-gradient-to-b from-blue-700 to-blue-500 text-white p-4 flex flex-col justify-between rounded-r-3xl shadow-xl">

//       {/* Logo */}
//       <h1 className="text-2xl font-bold mb-8">AI Diagnostics</h1>

//       {/* Menu */}
//       <div className="space-y-3">

//         {menu.map((item, i) => {
//           const Icon = item.icon
//           const isActive = active === item.name

//           return (
//             <div
//               key={i}
//               onClick={() => setActive(item.name)}
//               className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-200
              
//               ${isActive
//                 ? "bg-white text-blue-700 shadow-md"
//                 : "hover:bg-white/20"
//               }`}
//             >
//               <Icon size={18} />
//               <span>{item.name}</span>
//             </div>
//           )
//         })}

//       </div>

//       {/* Logout */}
//       <button
//         onClick={handleLogout}
//         className="bg-white text-blue-700 py-2 rounded-xl hover:bg-gray-100 transition"
//       >
//         Logout
//       </button>

//     </div>
//   )
// }

import { useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  Home,
  FileText,
  BarChart,
  Info,
  ScanLine,
  HeartPulse
} from "lucide-react"

const menu = [
  { name: "Dashboard", icon: Home },
  { name: "X-Ray Analysis", icon: ScanLine },
  { name: "MRI Analysis", icon: ScanLine },
  { name: "ECG Analysis", icon: HeartPulse },
  { name: "History", icon: FileText },
  { name: "Trends", icon: BarChart },
  { name: "About", icon: Info },
]

export default function Sidebar() {
  const [active, setActive] = useState("Dashboard")
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem("token")
    navigate("/")
  }

  return (
    <div className="w-64 h-screen bg-gradient-to-b from-blue-700 to-blue-500 text-white rounded-r-3xl shadow-xl flex flex-col">

      {/* Top */}
      <div className="p-5">
        <h1 className="text-2xl font-bold">AI Diagnostics</h1>
      </div>

      {/* Menu (fills space properly) */}
      <div className="flex-1 flex flex-col justify-evenly px-3">

        {menu.map((item, i) => {
          const Icon = item.icon
          const isActive = active === item.name

          return (
            <div
              key={i}
              onClick={() => setActive(item.name)}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl cursor-pointer transition-all duration-200
              
              ${isActive
                ? "bg-white text-blue-700 shadow-md"
                : "hover:bg-white/20"
              }`}
            >
              <Icon size={18} />
              <span className="font-medium">{item.name}</span>
            </div>
          )
        })}

      </div>

      {/* Bottom Logout */}
      <div className="p-4">
        <button
          onClick={handleLogout}
          className="w-full bg-white text-blue-700 py-2 rounded-xl hover:bg-gray-100 transition"
        >
          Logout
        </button>
      </div>

    </div>
  )
}