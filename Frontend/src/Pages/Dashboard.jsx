
// import Sidebar from "../components/Sidebar"
// import Navbar from "../components/Navbar"
// import StatCard from "../components/StatCard"
// import PatientTable from "../components/PatientTable"
// import { stats } from "../data/dummyData"

// function Dashboard() {
//   return (
//     <div className="flex bg-white min-h-screen">

//       {/* Sidebar */}
//       <Sidebar />

//       {/* Main Content */}
//       <div className="flex-1 bg-blue-50/40">

//         <Navbar />

//         <div className="p-8">

//           {/* Stats */}
//           <div className="grid grid-cols-3 gap-6 mb-8">
//             {stats.map((s, i) => (
//               <StatCard key={i} title={s.title} value={s.value} />
//             ))}
//           </div>

//           {/* Table */}
//           <PatientTable />

//         </div>
//       </div>

//     </div>
//   )
// }

// export default Dashboard

import { useState } from "react"
import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import StatCard from "../components/StatCard"
import PatientTable from "../components/PatientTable"
import XrayPage from "../components/XrayPage"
import { stats } from "../data/dummyData"

function Dashboard() {
  const [active, setActive] = useState("Dashboard")

  return (
    <div className="flex bg-white min-h-screen">
  
      <Sidebar active={active} setActive={setActive} />

      <div className="flex-1 bg-blue-50/40">

        <Navbar />

        <div className="p-8">

          {/* ✅ Dashboard View */}
          {active === "Dashboard" && (
            <>
              <div className="grid grid-cols-3 gap-6 mb-8">
                {stats.map((s, i) => (
                  <StatCard key={i} title={s.title} value={s.value} />
                ))}
              </div>

              <PatientTable />
            </>
          )}

          {/* ✅ X-Ray View */}
          {active === "X-Ray Analysis" && <XrayPage />}

        </div>

      </div>
    </div>
  )
}

export default Dashboard