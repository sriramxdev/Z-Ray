// import Sidebar from "../components/Sidebar"
// import Navbar from "../components/Navbar"
// import StatCard from "../components/StatCard"
// import PatientTable from "../components/PatientTable"
// import ChartCard from "../components/ChartCard"
// import { stats } from "../data/dummyData"

// function Dashboard(){

// return(

// <div className="flex bg-blue-50 min-h-screen">

// <Sidebar/>

// <div className="flex-1">

// <Navbar/>

// <div className="p-8">

// <div className="grid grid-cols-3 gap-6 mb-8">

// {stats.map((s,i)=>(
// <StatCard key={i} title={s.title} value={s.value}/>
// ))}

// </div>

// <PatientTable/>

// </div>

// </div>

// </div>

// )

// }

// export default Dashboard
import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import StatCard from "../components/StatCard"
import PatientTable from "../components/PatientTable"
import { stats } from "../data/dummyData"

function Dashboard() {
  return (
    <div className="flex bg-white min-h-screen">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 bg-blue-50/40">

        <Navbar />

        <div className="p-8">

          {/* Stats */}
          <div className="grid grid-cols-3 gap-6 mb-8">
            {stats.map((s, i) => (
              <StatCard key={i} title={s.title} value={s.value} />
            ))}
          </div>

          {/* Table */}
          <PatientTable />

        </div>
      </div>

    </div>
  )
}

export default Dashboard