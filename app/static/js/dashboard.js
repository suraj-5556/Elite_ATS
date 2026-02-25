/**
 * TalentAI - Dashboard JavaScript
 * Fetches score history via Fetch API and renders Chart.js visualization.
 */

"use strict";

document.addEventListener('DOMContentLoaded', async () => {
  const canvas = document.getElementById('scoreChart');
  if (!canvas) return;

  try {
    const res = await fetch('/dashboard/stats');
    if (!res.ok) throw new Error('Failed to fetch stats');
    const { scores } = await res.json();

    if (!scores || scores.length === 0) {
      canvas.closest('.card').style.display = 'none';
      return;
    }

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: scores.map(s => s.date),
        datasets: [
          {
            label: 'Final',
            data: scores.map(s => s.final),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99,102,241,0.1)',
            borderWidth: 2.5,
            pointRadius: 4,
            pointBackgroundColor: '#6366f1',
            tension: 0.4,
            fill: true,
          },
          {
            label: 'NLP',
            data: scores.map(s => s.nlp),
            borderColor: '#06b6d4',
            borderWidth: 1.5,
            pointRadius: 3,
            pointBackgroundColor: '#06b6d4',
            tension: 0.4,
            borderDash: [4, 2],
          },
          {
            label: 'ML',
            data: scores.map(s => s.ml),
            borderColor: '#10b981',
            borderWidth: 1.5,
            pointRadius: 3,
            pointBackgroundColor: '#10b981',
            tension: 0.4,
            borderDash: [4, 2],
          },
          {
            label: 'Claude',
            data: scores.map(s => s.claude),
            borderColor: '#f59e0b',
            borderWidth: 1.5,
            pointRadius: 3,
            pointBackgroundColor: '#f59e0b',
            tension: 0.4,
            borderDash: [4, 2],
          },
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#1a1d27',
            borderColor: 'rgba(255,255,255,0.1)',
            borderWidth: 1,
            titleColor: '#f1f5f9',
            bodyColor: '#94a3b8',
            callbacks: {
              label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y}%`
            }
          }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: { color: '#64748b', font: { size: 11 } }
          },
          y: {
            min: 0, max: 100,
            grid: { color: 'rgba(255,255,255,0.04)' },
            ticks: {
              color: '#64748b', font: { size: 11 },
              callback: v => v + '%'
            }
          }
        }
      }
    });

  } catch (err) {
    console.error('Dashboard chart error:', err);
    canvas.closest('.card').style.display = 'none';
  }
});
