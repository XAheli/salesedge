import { useParams } from "react-router-dom";

export default function DealDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Deal: {id}</h2>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card flex h-64 items-center justify-center p-6">
          <p className="text-sm text-text-tertiary">Deal timeline and risk factors</p>
        </div>
        <div className="card flex h-64 items-center justify-center p-6">
          <p className="text-sm text-text-tertiary">Stakeholder coverage heatmap</p>
        </div>
      </div>
    </div>
  );
}
