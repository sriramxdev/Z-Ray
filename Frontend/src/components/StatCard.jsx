// function StatCard({title,value}){

// return(

// <div className="bg-white p-6 rounded-xl shadow hover:shadow-lg transition">

// <h3 className="text-gray-500">{title}</h3>

// <p className="text-3xl font-bold text-blue-600 mt-2">
// {value}
// </p>

// </div>

// )

// }

// export default StatCard

export default function StatCard({ title, value }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-md hover:shadow-lg transition">

      <p className="text-gray-500">{title}</p>

      <h2 className="text-3xl font-bold text-blue-600 mt-2">
        {value}
      </h2>

    </div>
  )
}