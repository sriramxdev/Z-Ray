import { patients } from "../data/dummyData"

function PatientTable(){

return(

<table className="w-full bg-white rounded-xl shadow">

<thead className="bg-blue-600 text-white">
<tr>
<th className="p-3">Name</th>
<th className="p-3">Scan</th>
<th className="p-3">Result</th>
<th className="p-3">Date</th>
</tr>
</thead>

<tbody>

{patients.map((p,i)=>(
<tr key={i} className="text-center border-b">

<td className="p-3">{p.name}</td>
<td className="p-3">{p.scan}</td>
<td className="p-3">{p.result}</td>
<td className="p-3">{p.date}</td>

</tr>
))}

</tbody>

</table>

)

}

export default PatientTable