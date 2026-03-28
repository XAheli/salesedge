import { useParams } from "react-router-dom";

export default function ProspectDetail() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Prospect: {id}</h2>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card flex h-64 items-center justify-center p-6 lg:col-span-2">
          <p className="text-sm text-text-tertiary">Company profile and enrichment timeline</p>
        </div>
        <div className="card flex h-64 items-center justify-center p-6">
          <p className="text-sm text-text-tertiary">Fit score breakdown (radar chart)</p>
        </div>
      </div>
    </div>
  );
}
