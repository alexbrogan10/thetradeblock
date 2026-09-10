import { NavLink } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", label: "Front Office Dashboard" },
  { to: "/trade-center", label: "Trade Center" },
  { to: "/draft-capital", label: "Draft Capital" },
];

export function Sidebar() {
  return (
    <aside className="flex h-screen w-64 flex-shrink-0 flex-col border-r border-slate-200 bg-slate-950 text-slate-200">
      <div className="border-b border-slate-800 px-5 py-5">
        <div className="text-lg font-bold text-white">The Trade Block</div>
        <div className="text-xs text-slate-400">NFL Trade Analytics</div>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `block rounded px-3 py-2 text-sm font-medium transition ${
                isActive ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-900"
              }`
            }
            end={item.to === "/"}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-slate-800 px-4 py-3 text-[11px] leading-snug text-slate-500">
        Decision support only. Independent project — not affiliated with the
        NFL or any team. Demo data is synthetic, not official NFL data.
      </div>
    </aside>
  );
}
