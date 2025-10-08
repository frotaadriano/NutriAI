import React from "react";

export default function NutritionTable({ data }:{data:{name:string;per100g:number;portion:number}[]}) {
  return (
    <div style={{border:"1px solid #eee", borderRadius:12, padding:12, marginTop:16}}>
      <h3 style={{marginTop:0}}>Tabela Nutricional</h3>
      <table style={{width:"100%", borderCollapse:"collapse"}}>
        <thead>
          <tr>
            <th style={{textAlign:"left", borderBottom:"1px solid #eee"}}>Nutriente</th>
            <th style={{textAlign:"right", borderBottom:"1px solid #eee"}}>/100g</th>
            <th style={{textAlign:"right", borderBottom:"1px solid #eee"}}>Porção</th>
          </tr>
        </thead>
        <tbody>
          {data.map((n,i)=>(
            <tr key={i}>
              <td style={{padding:"6px 0"}}>{n.name}</td>
              <td style={{textAlign:"right"}}>{n.per100g}</td>
              <td style={{textAlign:"right"}}>{n.portion}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
