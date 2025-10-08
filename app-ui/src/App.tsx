import React, { useState } from "react";
import NutritionTable from "./NutritionTable";

type Nutrient = { name: string; per100g: number; portion: number };
type Output = {
    nutrients: Nutrient[];
    insights: string[];
    advice: string;
    disclaimer: string;
};

export default function App() {
    const [desc, setDesc] = useState("");
    const [portion, setPortion] = useState<string>("");
    const [data, setData] = useState<Output | null>(null);
    const [loading, setLoading] = useState(false);
    const [err, setErr] = useState<string | null>(null);

    const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true); setErr(null); setData(null);
        try {
            const res = await fetch(`${API_BASE}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    food_description: desc,
                    portion_grams: portion ? Number(portion) : null
                })
            });
            if (!res.ok) throw new Error("Falha ao analisar alimento.");
            const json: Output = await res.json();
            setData(json);
        } catch (e: any) {
            setErr(e.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: 720, margin: "40px auto", fontFamily: "system-ui" }}>
            <h1>NutriAI</h1>
            <p>Descreva o alimento e (opcional) a porção em gramas.</p>

            <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
                <input
                    placeholder="Ex.: tapioca 2 colheres com queijo"
                    value={desc}
                    onChange={e => setDesc(e.target.value)}
                    required
                />
                <input
                    placeholder="Porção em gramas (opcional, ex.: 120)"
                    value={portion}
                    onChange={e => setPortion(e.target.value)}
                />
                <button disabled={loading}>{loading ? "Analisando..." : "Analisar"}</button>
            </form>

            {err && <p style={{ color: "crimson" }}>{err}</p>}
            {data && (
                <div style={{ marginTop: 16 }}>
                    <NutritionTable data={data.nutrients} />
                    <ul>
                        {data.insights.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                    <p><strong>Dica:</strong> {data.advice}</p>
                    <p style={{ fontSize: 12, opacity: .7 }}>{data.disclaimer}</p>
                </div>
            )}
        </div>
    );
}
