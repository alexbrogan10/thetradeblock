import type { ReactNode } from "react";

export function Card({
  title,
  children,
  className = "",
  actions,
}: {
  title?: string;
  children: ReactNode;
  className?: string;
  actions?: ReactNode;
}) {
  return (
    <div className={`rounded-lg border border-slate-200 bg-white shadow-sm ${className}`}>
      {title && (
        <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            {title}
          </h3>
          {actions}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
