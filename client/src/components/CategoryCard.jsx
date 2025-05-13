import { FaArrowRight } from 'react-icons/fa';

const CategoryCard = ({ category }) => {
  return (
    <div className="flex flex-col items-center bg-gray-50 border rounded-xl p-4 w-28 hover:shadow hover:bg-white transition">
      <img src={category.icon} alt={category.name} className="w-10 h-10 mb-2" />
      <span className="text-sm text-center font-medium">{category.name}</span>
      <FaArrowRight className="text-xs text-gray-500 mt-2" />
    </div>
  );
};

export default CategoryCard;
