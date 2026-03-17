import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import StatCard from "../components/StatCard"
import PatientTable from "../components/PatientTable"
import ChartCard from "../components/ChartCard"
import { stats } from "../data/dummyData"

function Dashboard(){

return(

<div className="flex bg-blue-50 min-h-screen">

<Sidebar/>

<div className="flex-1">

<Navbar/>

<div className="p-8">

<div className="grid grid-cols-3 gap-6 mb-8">

{stats.map((s,i)=>(
<StatCard key={i} title={s.title} value={s.value}/>
))}

</div>

<PatientTable/>

</div>

</div>

</div>

)

}

export default Dashboard