import { useMemo, useState } from 'react';
import { areas, contexts, movements, protocols, type Area, type Context, type Movement, type Protocol } from './data';
import { cn } from './lib/cn';

const timeOptions = ['1 min', '2 min', '3 min', '5 min', '10 min', '20 min'] as const;

type TimeOption = (typeof timeOptions)[number];

function App() {
  const [selectedContext, setSelectedContext] = useState<Context>('desk');
  const [selectedArea, setSelectedArea] = useState<Area | 'all'>('all');
  const [selectedTime, setSelectedTime] = useState<TimeOption | 'any'>('any');
  const [query, setQuery] = useState('');
  const [selectedMovementId, setSelectedMovementId] = useState(movements[0].id);

  const filteredMovements = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return movements.filter((movement) => {
      const matchesContext = movement.contexts.includes(selectedContext);
      const matchesArea = selectedArea === 'all' || movement.area.includes(selectedArea);
      const matchesTime = selectedTime === 'any' || movement.time === selectedTime;
      const matchesQuery =
        normalizedQuery.length === 0 ||
        [movement.title, movement.useWhen, movement.dose, movement.source, movement.area.join(' ')]
          .join(' ')
          .toLowerCase()
          .includes(normalizedQuery);

      return matchesContext && matchesArea && matchesTime && matchesQuery;
    });
  }, [query, selectedArea, selectedContext, selectedTime]);

  const selectedMovement = movements.find((movement) => movement.id === selectedMovementId) ?? filteredMovements[0] ?? movements[0];
  const contextProtocols = protocols.filter((protocol) => protocol.context === selectedContext);

  return (
    <main className="min-h-dvh bg-slate-50 text-slate-950">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <Header />

        <section className="grid gap-4 lg:grid-cols-[18rem_minmax(0,1fr)_24rem]">
          <aside className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm lg:sticky lg:top-6 lg:self-start">
            <ContextPicker selectedContext={selectedContext} onSelect={setSelectedContext} />
            <FilterBlock
              selectedArea={selectedArea}
              selectedTime={selectedTime}
              query={query}
              onAreaChange={setSelectedArea}
              onTimeChange={setSelectedTime}
              onQueryChange={setQuery}
            />
          </aside>

          <section className="flex min-w-0 flex-col gap-4">
            <ProtocolShelf protocols={contextProtocols} selectedMovementId={selectedMovement.id} onSelectMovement={setSelectedMovementId} />
            <MovementGrid movements={filteredMovements} selectedMovementId={selectedMovement.id} onSelectMovement={setSelectedMovementId} />
          </section>

          <aside className="lg:sticky lg:top-6 lg:self-start">
            <MovementDetail movement={selectedMovement} />
          </aside>
        </section>
      </div>
    </main>
  );
}

function Header() {
  return (
    <header className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="max-w-3xl">
          <p className="text-sm font-medium text-sky-700">XF Movement Library</p>
          <h1 className="mt-2 text-balance text-3xl font-semibold text-slate-950 sm:text-4xl">
            Recall the right movement before YouTube steals the vibe.
          </h1>
          <p className="mt-3 max-w-2xl text-pretty text-sm leading-6 text-slate-600 sm:text-base">
            Expert-sourced movement cards for desk shoulders, sticky hips, early CrossFit, floor capacity, and dad-safe basics.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-2 rounded-2xl bg-slate-100 p-2 text-center text-xs text-slate-600 sm:min-w-80">
          <Metric label="Cards" value="10" />
          <Metric label="Protocols" value="4" />
          <Metric label="Rabbit holes" value="0" />
        </div>
      </div>
    </header>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-white px-3 py-2 shadow-sm">
      <div className="tabular-nums text-lg font-semibold text-slate-950">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}

function ContextPicker({ selectedContext, onSelect }: { selectedContext: Context; onSelect: (context: Context) => void }) {
  return (
    <section>
      <h2 className="text-sm font-semibold text-slate-950">What are we solving?</h2>
      <div className="mt-3 grid gap-2">
        {contexts.map((context) => (
          <button
            key={context.id}
            type="button"
            onClick={() => onSelect(context.id)}
            className={cn(
              'rounded-2xl border px-3 py-3 text-left shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2',
              selectedContext === context.id
                ? 'border-sky-200 bg-sky-50 text-sky-950'
                : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
            )}
          >
            <span className="block text-sm font-medium">{context.label}</span>
            <span className="mt-1 block text-xs text-slate-500">{context.helper}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

function FilterBlock({
  selectedArea,
  selectedTime,
  query,
  onAreaChange,
  onTimeChange,
  onQueryChange,
}: {
  selectedArea: Area | 'all';
  selectedTime: TimeOption | 'any';
  query: string;
  onAreaChange: (area: Area | 'all') => void;
  onTimeChange: (time: TimeOption | 'any') => void;
  onQueryChange: (query: string) => void;
}) {
  return (
    <section className="mt-6 border-t border-slate-200 pt-5">
      <label htmlFor="movement-search" className="text-sm font-semibold text-slate-950">
        Quick search
      </label>
      <input
        id="movement-search"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        placeholder="couch, hang, breath..."
        className="mt-2 w-full rounded-2xl border border-slate-200 bg-white px-3 py-3 text-sm text-slate-950 shadow-sm outline-none placeholder:text-slate-400 focus:border-sky-400 focus:ring-2 focus:ring-sky-100"
      />

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-slate-950">Body map</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          <Chip selected={selectedArea === 'all'} onClick={() => onAreaChange('all')}>
            All
          </Chip>
          {areas.map((area) => (
            <Chip key={area.id} selected={selectedArea === area.id} onClick={() => onAreaChange(area.id)}>
              {area.label}
            </Chip>
          ))}
        </div>
      </div>

      <div className="mt-5">
        <h3 className="text-sm font-semibold text-slate-950">Time</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          <Chip selected={selectedTime === 'any'} onClick={() => onTimeChange('any')}>
            Any
          </Chip>
          {timeOptions.map((time) => (
            <Chip key={time} selected={selectedTime === time} onClick={() => onTimeChange(time)}>
              {time}
            </Chip>
          ))}
        </div>
      </div>
    </section>
  );
}

function Chip({ selected, onClick, children }: { selected: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded-full border px-3 py-2 text-xs font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2',
        selected ? 'border-sky-200 bg-sky-100 text-sky-950' : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
      )}
    >
      {children}
    </button>
  );
}

function ProtocolShelf({
  protocols,
  selectedMovementId,
  onSelectMovement,
}: {
  protocols: Protocol[];
  selectedMovementId: string;
  onSelectMovement: (movementId: string) => void;
}) {
  if (protocols.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-950">No protocol yet</h2>
        <p className="mt-1 text-sm text-slate-600">Pick a movement card below and turn it into the first protocol.</p>
      </div>
    );
  }

  return (
    <section className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-sm font-semibold text-slate-950">Tiny flows</h2>
          <p className="text-xs text-slate-500">Three cards max in spirit. No rabbit holes.</p>
        </div>
      </div>
      <div className="mt-3 grid gap-3 xl:grid-cols-2">
        {protocols.map((protocol) => (
          <article key={protocol.id} className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-950">{protocol.title}</h3>
                <p className="mt-1 text-pretty text-xs leading-5 text-slate-600">{protocol.promise}</p>
              </div>
              <span className="rounded-full bg-white px-2 py-1 text-xs font-medium tabular-nums text-slate-600 shadow-sm">{protocol.duration}</span>
            </div>
            <ol className="mt-3 grid gap-2">
              {protocol.steps.map((step, index) => {
                const movement = movements.find((item) => item.id === step.movementId);
                if (!movement) return null;

                return (
                  <li key={step.movementId}>
                    <button
                      type="button"
                      onClick={() => onSelectMovement(step.movementId)}
                      className={cn(
                        'flex w-full items-center justify-between gap-3 rounded-xl border px-3 py-2 text-left text-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2',
                        selectedMovementId === step.movementId
                          ? 'border-sky-200 bg-sky-50 text-sky-950'
                          : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50',
                      )}
                    >
                      <span className="min-w-0 truncate">
                        <span className="mr-2 text-xs tabular-nums text-slate-400">{index + 1}</span>
                        {movement.title}
                      </span>
                      <span className="shrink-0 text-xs tabular-nums text-slate-500">{step.dose}</span>
                    </button>
                  </li>
                );
              })}
            </ol>
          </article>
        ))}
      </div>
    </section>
  );
}

function MovementGrid({
  movements,
  selectedMovementId,
  onSelectMovement,
}: {
  movements: Movement[];
  selectedMovementId: string;
  onSelectMovement: (movementId: string) => void;
}) {
  if (movements.length === 0) {
    return (
      <section className="rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <h2 className="text-balance text-lg font-semibold text-slate-950">No cards for that filter yet.</h2>
        <p className="mx-auto mt-2 max-w-md text-pretty text-sm text-slate-600">Clear search or choose All body areas. Next action: add the missing card from a trusted source.</p>
      </section>
    );
  }

  return (
    <section className="grid gap-3 md:grid-cols-2">
      {movements.map((movement) => (
        <button
          key={movement.id}
          type="button"
          onClick={() => onSelectMovement(movement.id)}
          className={cn(
            'rounded-3xl border bg-white p-4 text-left shadow-sm focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2',
            selectedMovementId === movement.id ? 'border-sky-300 ring-1 ring-sky-200' : 'border-slate-200 hover:bg-slate-50',
          )}
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <h3 className="truncate text-base font-semibold text-slate-950">{movement.title}</h3>
              <p className="mt-1 line-clamp-2 text-pretty text-sm leading-5 text-slate-600">{movement.useWhen}</p>
            </div>
            <span className="shrink-0 rounded-full bg-slate-100 px-2 py-1 text-xs font-medium tabular-nums text-slate-600">{movement.time}</span>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {movement.area.map((area) => (
              <span key={area} className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-600">
                {area}
              </span>
            ))}
            {movement.dadSafe ? <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">dad-safe</span> : null}
          </div>
        </button>
      ))}
    </section>
  );
}

function MovementDetail({ movement }: { movement: Movement }) {
  return (
    <article className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium uppercase text-sky-700">Movement card</p>
          <h2 className="mt-1 text-balance text-2xl font-semibold text-slate-950">{movement.title}</h2>
        </div>
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium tabular-nums text-slate-700">{movement.time}</span>
      </div>

      <section className="mt-5 rounded-2xl bg-slate-50 p-4">
        <h3 className="text-sm font-semibold text-slate-950">Use when</h3>
        <p className="mt-1 text-pretty text-sm leading-6 text-slate-600">{movement.useWhen}</p>
      </section>

      <section className="mt-4">
        <h3 className="text-sm font-semibold text-slate-950">Dose</h3>
        <p className="mt-1 text-pretty text-sm leading-6 tabular-nums text-slate-600">{movement.dose}</p>
      </section>

      <section className="mt-4">
        <h3 className="text-sm font-semibold text-slate-950">Three cues</h3>
        <ul className="mt-2 grid gap-2">
          {movement.cues.map((cue) => (
            <li key={cue} className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm leading-6 text-slate-700">
              {cue}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-4 grid gap-3">
        <Callout title="Common miss" body={movement.mistake} tone="amber" />
        <Callout title="Retest" body={movement.retest} tone="sky" />
      </section>

      <footer className="mt-5 border-t border-slate-200 pt-4">
        <h3 className="text-sm font-semibold text-slate-950">Source</h3>
        <p className="mt-1 text-pretty text-xs leading-5 text-slate-500">{movement.source}</p>
      </footer>
    </article>
  );
}

function Callout({ title, body, tone }: { title: string; body: string; tone: 'amber' | 'sky' }) {
  return (
    <div className={cn('rounded-2xl border p-3', tone === 'amber' ? 'border-amber-200 bg-amber-50' : 'border-sky-200 bg-sky-50')}>
      <h3 className={cn('text-sm font-semibold', tone === 'amber' ? 'text-amber-950' : 'text-sky-950')}>{title}</h3>
      <p className={cn('mt-1 text-pretty text-sm leading-6', tone === 'amber' ? 'text-amber-800' : 'text-sky-800')}>{body}</p>
    </div>
  );
}

export default App;
