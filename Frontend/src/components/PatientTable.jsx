// import { patients } from "../data/dummyData"

// function PatientTable(){

// return(

// <table className="w-full bg-white rounded-xl shadow">

// <thead className="bg-blue-600 text-white">
// <tr>
// <th className="p-3">Name</th>
// <th className="p-3">Scan</th>
// <th className="p-3">Result</th>
// <th className="p-3">Date</th>
// </tr>
// </thead>

// <tbody>

// {patients.map((p,i)=>(
// <tr key={i} className="text-center border-b">

// <td className="p-3">{p.name}</td>
// <td className="p-3">{p.scan}</td>
// <td className="p-3">{p.result}</td>
// <td className="p-3">{p.date}</td>

// </tr>
// ))}

// </tbody>

// </table>

// )

// }

// export default PatientTable

export default function PatientTable() {
  return (
    <div className="bg-white rounded-2xl shadow-md overflow-hidden">

      <table className="w-full text-left">

        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="p-4">Name</th>
            <th className="p-4">Scan</th>
            <th className="p-4">Result</th>
            <th className="p-4">Date</th>
          </tr>
        </thead>

        <tbody>
          <tr className="border-b hover:bg-gray-50">
            <td className="p-4">Rahul</td>
            <td className="p-4">X-ray</td>
            <td className="p-4">Normal</td>
            <td className="p-4">12 Mar</td>
          </tr>

          <tr className="border-b hover:bg-gray-50">
            <td className="p-4">Anita</td>
            <td className="p-4">MRI</td>
            <td className="p-4">Tumor</td>
            <td className="p-4">13 Mar</td>
          </tr>

          <tr className="hover:bg-gray-50">
            <td className="p-4">John</td>
            <td className="p-4">ECG</td>
            <td className="p-4">Arrhythmia</td>
            <td className="p-4">14 Mar</td>
          </tr>
        </tbody>

      </table>

    </div>
  )
}