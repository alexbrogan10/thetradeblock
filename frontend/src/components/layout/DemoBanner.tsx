export function DemoBanner({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <div className="border-b border-amber-300 bg-amber-50 px-4 py-1.5 text-center text-xs font-semibold tracking-wide text-amber-800">
      DEMO DATA — NOT OFFICIAL NFL DATA. Players, stats, and contracts shown are synthetic.
    </div>
  );
}
