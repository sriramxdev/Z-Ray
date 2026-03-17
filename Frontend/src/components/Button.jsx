export default function Button({ text }) {
  return (
    <button className="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition duration-300 shadow-md hover:scale-105">
      {text}
    </button>
  );
}