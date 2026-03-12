<script lang="ts">
	import { page } from '$app/state';
	import { replaceState } from '$app/navigation';
	import { getOccupation, getElementDescriptions, type OccupationDetail } from '$lib/api/client';
	import RatedBars from '$lib/components/RatedBars.svelte';
	import Tooltip from '$lib/components/Tooltip.svelte';

	let occ = $state<OccupationDetail | null>(null);
	let descriptions = $state<Record<string, string>>({});
	let loading = $state(true);
	let error = $state('');
	let activeSection = $state('tasks');

	const sections = [
		{ id: 'tasks', label: 'Tasks', desc: 'Specific duties and responsibilities typically performed by workers in this occupation.' },
		{ id: 'skills', label: 'Skills', desc: 'Developed capacities that facilitate learning or the performance of activities across jobs, including foundational skills like reading and critical thinking, and cross-functional skills like problem solving and communication.' },
		{ id: 'abilities', label: 'Abilities', desc: 'Enduring personal attributes that influence job performance, including cognitive, psychomotor, physical, and sensory capabilities.' },
		{ id: 'knowledge', label: 'Knowledge', desc: 'Organised sets of principles and facts relevant to this occupation, spanning domains such as business, science, engineering, and more.' },
		{ id: 'technology', label: 'Technology', desc: 'Software, programming languages, and information technology tools commonly used in this occupation.' },
		{ id: 'tools', label: 'Tools', desc: 'Machines, equipment, and physical tools essential to the performance of this occupation.' },
		{ id: 'activities', label: 'Work activities', desc: 'General work activities common across many occupations, describing the broad types of job tasks performed.' },
		{ id: 'detailed-activities', label: 'Detailed activities', desc: 'Specific work activities performed within this occupation, weighted by relevance.' },
		{ id: 'context', label: 'Work context', desc: 'Physical and social factors that influence the nature of work, including interpersonal relationships, physical conditions, and structural characteristics of the job.' },
		{ id: 'styles', label: 'Work styles', desc: 'Personal characteristics and work habits that can affect how well someone performs in this role.' },
		{ id: 'interests', label: 'Interests', desc: "Occupational interest profile based on Holland's RIASEC model, indicating the types of work environments and activities best suited to this occupation." },
		{ id: 'values', label: 'Work values', desc: 'Work needs and values that are most important and well-satisfied in this occupation.' },
		{ id: 'education', label: 'Education', desc: 'Typical education level, training, and experience requirements for entry into this occupation.' },
		{ id: 'related', label: 'Related', desc: 'Other occupations with similar skill, knowledge, and work activity profiles.' },
		{ id: 'sources', label: 'Sources', desc: 'The US O*NET source occupations whose data was combined to create this UK occupation profile. Click any row to view it on O*NET Online.' },
	];

	const RIASEC_NAMES = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional'];

	const EDU_CATEGORY_LABELS: Record<string, Record<number, string>> = {
		RL: {
			1: 'Less than High School', 2: 'High School Diploma', 3: 'Post-Secondary Certificate',
			4: 'Some College', 5: "Associate's Degree", 6: "Bachelor's Degree",
			7: 'Post-Baccalaureate Certificate', 8: "Master's Degree", 9: "Post-Master's Certificate",
			10: 'First Professional Degree', 11: 'Doctoral Degree', 12: 'Post-Doctoral Training',
		},
		RW: {
			1: 'None', 2: 'Up to 1 month', 3: '1–3 months', 4: '3–6 months',
			5: '6 months – 1 year', 6: '1–2 years', 7: '2–4 years',
			8: '4–6 years', 9: '6–8 years', 10: '8–10 years', 11: 'Over 10 years',
		},
		PT: {
			1: 'None', 2: 'Up to 1 month', 3: '1–3 months', 4: '3–6 months',
			5: '6 months – 1 year', 6: '1–2 years', 7: '2–4 years',
			8: '4–6 years', 9: 'Over 6 years',
		},
		OJ: {
			1: 'None', 2: 'Up to 1 month', 3: '1–3 months', 4: '3–6 months',
			5: '6 months – 1 year', 6: '1–2 years', 7: '2–4 years',
			8: '4–6 years', 9: 'Over 6 years',
		},
	};

	function groupEducation(education: any[]): { name: string; scaleId: string; items: { label: string; value: number }[] }[] {
		const groups = new Map<string, { name: string; scaleId: string; items: { label: string; value: number }[] }>();
		for (const edu of education) {
			const name = edu['Element Name'] ?? edu.Element_Name ?? '';
			const scaleId = edu['Scale ID'] ?? edu.Scale_ID ?? '';
			const cat = Math.round(edu.Category ?? 0);
			const val = edu['Data Value'] ?? 0;
			if (!groups.has(name)) groups.set(name, { name, scaleId, items: [] });
			const labels = EDU_CATEGORY_LABELS[scaleId] ?? {};
			groups.get(name)!.items.push({ label: labels[cat] ?? `Category ${cat}`, value: val });
		}
		return [...groups.values()];
	}

	const sectionIds = sections.map(s => s.id);

	function sectionFromHash(): string {
		if (typeof window === 'undefined') return 'tasks';
		const hash = window.location.hash.replace('#', '');
		return sectionIds.includes(hash) ? hash : 'tasks';
	}

	$effect(() => {
		const code = Number(page.params.code);
		loading = true;
		error = '';
		activeSection = sectionFromHash();
		Promise.all([getOccupation(code), getElementDescriptions()])
			.then(([data, descs]) => { occ = data; descriptions = descs; loading = false; })
			.catch((e) => { error = e.message; loading = false; });
	});

	function setSection(id: string) {
		activeSection = id;
		if (typeof window !== 'undefined') {
			replaceState(`${window.location.pathname}#${id}`, {});
		}
	}

	function jobZoneLabel(jz: number): string {
		const labels: Record<number, string> = {
			1: 'Little to some preparation needed',
			2: 'Little to some preparation needed',
			3: 'Medium preparation needed',
			4: 'Considerable preparation needed',
			5: 'Extensive preparation needed',
		};
		return labels[jz] || `Zone ${jz}`;
	}

	function jobZoneDisplay(jz: number): string {
		return jz <= 2 ? '1–2' : String(jz);
	}

	function getRiasecCode(): string {
		if (!occ?.interests) return '';
		const sorted = [...occ.interests]
			.filter(i => RIASEC_NAMES.includes(i.element_name))
			.sort((a, b) => ((b as any).value_OI ?? 0) - ((a as any).value_OI ?? 0));
		return sorted.slice(0, 3).map(i => i.element_name[0]).join('');
	}

	function sortedByImportance(items: any[], limit?: number) {
		const sorted = [...items].sort((a, b) => (b.value_IM ?? 0) - (a.value_IM ?? 0));
		return limit ? sorted.slice(0, limit) : sorted;
	}

</script>

<svelte:head>
	{#if occ}<title>{occ.title} - ASPECTT</title>{/if}
</svelte:head>

<div class="container">
	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if error}
		<div class="card"><p class="error">{error}</p></div>
	{:else if occ}
		<div class="occ-header">
			<div class="occ-code">{occ.uk_soc_2020}</div>
			<div class="occ-info">
				<h1>{occ.title}</h1>
				<p class="occ-desc">{occ.description}</p>
				<div class="header-tags">
					{#if occ.job_zone}
						<span class="header-tag jz">Job Zone {jobZoneDisplay(occ.job_zone)}</span>
					{/if}
					{#if getRiasecCode()}
						<span class="header-tag riasec">{getRiasecCode()}</span>
					{/if}
					<button class="header-tag source" onclick={() => setSection('sources')}>{occ.source_occupations?.length ?? 0} source occupations</button>
				</div>
			</div>
		</div>

		{#if occ.insufficient_source_data}
			<div class="data-warning">
				<strong>Data quality notice:</strong> {occ.insufficient_source_data}
			</div>
		{/if}

		<div class="layout">
			<nav class="sidebar">
				{#each sections as sec}
					<button class="nav-item" class:active={activeSection === sec.id}
						onclick={() => setSection(sec.id)}>
						{sec.label}
					</button>
				{/each}
				<hr class="nav-divider" />
				<a href="/compare?code={occ.uk_soc_2020}" class="nav-item compare-link">Compare...</a>
			</nav>

			<div class="content">
				{#if sections.find(s => s.id === activeSection)?.desc}
					<p class="section-desc">{sections.find(s => s.id === activeSection)?.desc}</p>
				{/if}

				{#if activeSection === 'tasks'}
					{#if occ.emerging_tasks?.length}
						<div class="card emerging-card">
							<h2>Emerging tasks ({occ.emerging_tasks.length})</h2>
							<div class="task-items">
								{#each occ.emerging_tasks as et}
									<div class="task-item">
										<div class="task-content">
											<span class="task-text">{et.task}</span>
											<span class="task-badges">
												<span class="badge emerging-{et.category.toLowerCase()}">{et.category}</span>
											</span>
										</div>
									</div>
								{/each}
							</div>
						</div>
					{/if}

					<div class="card">
						<h2>Tasks ({occ.tasks?.length ?? 0})</h2>
						{#if occ.tasks?.length}
							<div class="task-items">
								{#each occ.tasks as task}
									<div class="task-item">
										<div class="task-content">
											<span class="task-text">{task.task}</span>
											<span class="task-badges">
												{#if task.task_type === 'Core'}<span class="badge">Core</span>
												{:else if task.task_type === 'Supplemental'}<span class="badge supplemental">Supplemental</span>
												{:else if task.task_type === 'Unclassified'}<span class="badge unclassified">Unclassified</span>
												{/if}
											</span>
										</div>
									</div>
								{/each}
							</div>
						{:else}
							<p class="muted">No task data available</p>
						{/if}
					</div>

				{:else if activeSection === 'skills'}
					<div class="card">
						<h2>Skills ({occ.skills?.length ?? 0})</h2>
						{#if occ.skills?.length}
							<RatedBars items={sortedByImportance(occ.skills)} {descriptions} />
						{:else}<p class="muted">No skills data available</p>{/if}
					</div>

				{:else if activeSection === 'abilities'}
					<div class="card">
						<h2>Abilities ({occ.abilities?.length ?? 0})</h2>
						{#if occ.abilities?.length}
							<RatedBars items={sortedByImportance(occ.abilities)} {descriptions} />
						{:else}<p class="muted">No abilities data available</p>{/if}
					</div>

				{:else if activeSection === 'knowledge'}
					<div class="card">
						<h2>Knowledge ({occ.knowledge?.length ?? 0})</h2>
						{#if occ.knowledge?.length}
							<RatedBars items={sortedByImportance(occ.knowledge)} {descriptions} />
						{:else}<p class="muted">No knowledge data available</p>{/if}
					</div>

				{:else if activeSection === 'technology'}
					<div class="card">
						<h2>Technology ({occ.technology_skills?.length ?? 0})</h2>
						{#if occ.technology_skills?.length}
							<div class="tech-grid">
								{#each occ.technology_skills as tech}
									<span class="tech-tag">{tech.name}</span>
								{/each}
							</div>
						{:else}<p class="muted">No technology skills data available</p>{/if}
					</div>

				{:else if activeSection === 'tools'}
					<div class="card">
						<h2>Tools and equipment ({occ.tools_used?.length ?? 0})</h2>
						{#if occ.tools_used?.length}
							<div class="tech-grid">
								{#each occ.tools_used as tool}
									<span class="tech-tag">{tool.name}</span>
								{/each}
							</div>
						{:else}<p class="muted">No tools data available</p>{/if}
					</div>

				{:else if activeSection === 'activities'}
					<div class="card">
						<h2>Work activities ({occ.work_activities?.length ?? 0})</h2>
						{#if occ.work_activities?.length}
							<RatedBars items={sortedByImportance(occ.work_activities)} {descriptions} />
						{:else}<p class="muted">No work activities data available</p>{/if}
					</div>

				{:else if activeSection === 'detailed-activities'}
					<div class="card">
						<h2>Detailed work activities ({occ.detailed_work_activities?.length ?? 0})</h2>
						{#if occ.detailed_work_activities?.length}
							{@const sorted = [...occ.detailed_work_activities].sort((a, b) => b.weight - a.weight)}
							{@const maxWeight = sorted[0]?.weight ?? 1}
							<div class="dwa-list">
								{#each sorted as dwa}
									<div class="dwa-row">
										<span class="dwa-label">{dwa.title}</span>
										<div class="dwa-bar-track">
											<div class="dwa-bar-fill" style="width: {(dwa.weight / maxWeight) * 100}%"></div>
										</div>
										<span class="dwa-val">{dwa.weight.toFixed(1)}</span>
									</div>
								{/each}
							</div>
						{:else}<p class="muted">No detailed work activities data available</p>{/if}
					</div>

				{:else if activeSection === 'context'}
					<div class="card">
						<h2>Work context ({occ.work_context?.length ?? 0})</h2>
						{#if occ.work_context?.length}
							<RatedBars items={occ.work_context} showLevel={false} {descriptions} />
						{:else}<p class="muted">No work context data available</p>{/if}
					</div>

				{:else if activeSection === 'styles'}
					<div class="card">
						<h2>Work styles ({occ.work_styles?.length ?? 0})</h2>
						{#if occ.work_styles?.length}
							<RatedBars items={occ.work_styles} showLevel={false} {descriptions} />
						{:else}<p class="muted">No work styles data available</p>{/if}
					</div>

				{:else if activeSection === 'interests'}
					<div class="card">
						<h2>Interests</h2>
						{#if occ.interests?.length}
							{@const riasecItems = occ.interests.filter(i => RIASEC_NAMES.includes(i.element_name))}
							<div class="interest-bars">
								{#each riasecItems.sort((a, b) => ((b as any).value_OI ?? 0) - ((a as any).value_OI ?? 0)) as interest}
									{@const val = (interest as any).value_OI ?? 0}
									<div class="interest-row">
										<span class="interest-code" title={interest.element_name}>{interest.element_name[0]}</span>
										{#if descriptions[interest.element_id]}
										<span class="interest-name"><Tooltip text={descriptions[interest.element_id]}>{interest.element_name}</Tooltip></span>
									{:else}
										<span class="interest-name">{interest.element_name}</span>
									{/if}
										<div class="interest-bar-track">
											<div class="interest-bar-fill" style="width: {(val / 7) * 100}%"></div>
										</div>
										<span class="interest-val">{val.toFixed(1)}</span>
									</div>
								{/each}
							</div>
							<p class="riasec-label">RIASEC Code: <strong>{getRiasecCode()}</strong></p>
						{:else}<p class="muted">No interests data available</p>{/if}
					</div>

				{:else if activeSection === 'values'}
					<div class="card">
						<h2>Work values</h2>
						{#if occ.work_values?.length}
							{@const valueItems = occ.work_values.filter(v => !v.element_name.includes('High-Point'))}
							<div class="interest-bars">
								{#each valueItems.sort((a, b) => ((b as any).value_EX ?? 0) - ((a as any).value_EX ?? 0)) as wv}
									{@const val = (wv as any).value_EX ?? 0}
									<div class="interest-row">
										{#if descriptions[wv.element_id]}
										<span class="interest-name wv-name"><Tooltip text={descriptions[wv.element_id]}>{wv.element_name}</Tooltip></span>
									{:else}
										<span class="interest-name wv-name">{wv.element_name}</span>
									{/if}
										<div class="interest-bar-track">
											<div class="interest-bar-fill wv-fill" style="width: {(val / 7) * 100}%"></div>
										</div>
										<span class="interest-val">{val.toFixed(1)}</span>
									</div>
								{/each}
							</div>
						{:else}<p class="muted">No work values data available</p>{/if}
					</div>

				{:else if activeSection === 'education'}
					<div class="card">
						<h2>Education and training</h2>
						{#if occ.job_zone}
							<div class="job-zone">
								<strong>Job Zone {jobZoneDisplay(occ.job_zone)}:</strong> {jobZoneLabel(occ.job_zone)}
							</div>
						{/if}
						{#if occ.education?.length}
							{@const groups = groupEducation(occ.education)}
							{#each groups as group}
								<h3 class="edu-group-title">{group.name}</h3>
								<div class="edu-list">
									{#each group.items as item}
										<div class="edu-row">
											<span class="edu-label">{item.label}</span>
											<div class="bar-track">
												<div class="bar-fill importance" style="width: {Math.min(item.value, 100)}%"></div>
											</div>
											<span class="bar-value">{item.value.toFixed(1)}%</span>
										</div>
									{/each}
								</div>
							{/each}
						{:else}<p class="muted">No education data available</p>{/if}
					</div>

				{:else if activeSection === 'related'}
					<div class="card">
						<h2>Related occupations ({occ.related_occupations?.length ?? 0})</h2>
						{#if occ.related_occupations?.length}
							<div class="related-list">
								{#each occ.related_occupations as rel}
									<a class="related-item" href="/occupation/{rel.related_uk_soc}">
										<span class="related-code">{rel.related_uk_soc}</span>
										<span>{rel.related_uk_title}</span>
									</a>
								{/each}
							</div>
						{:else}<p class="muted">No related occupations data available</p>{/if}
					</div>

				{:else if activeSection === 'sources'}
					<div class="card">
						<h2>Source occupations ({occ.source_occupations?.length ?? 0})</h2>
						{#if occ.source_occupations?.length}
							<div class="source-list">
								{#each occ.source_occupations as src}
									{@const pct = src.weight * 100}
									<a class="source-card" href="https://www.onetonline.org/link/summary/{src.onet_soc}" target="_blank" rel="noopener">
										<div class="source-card-top">
											<span class="mono source-code">{src.onet_soc}</span>
											<span class="source-title">{src.onet_title}</span>
											<span class="source-weight">{pct.toFixed(1)}%</span>
										</div>
										<div class="source-bar-track">
											<div class="source-bar-fill" style="width: {pct}%"></div>
										</div>
									</a>
								{/each}
							</div>
						{:else}<p class="muted">No source occupation data available</p>{/if}
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.occ-header {
		display: flex; gap: 1.75rem; align-items: flex-start; margin-bottom: 1.25rem;
		background: var(--color-surface); padding: 1.75rem; border-radius: var(--radius-lg); border: 1px solid var(--color-border);
		box-shadow: var(--shadow-xs);
	}
	.occ-code {
		font-size: 1.75rem; font-weight: 700; color: var(--color-accent-bright); font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		flex: 0 0 auto; padding: 0.625rem 1.125rem; background: var(--color-accent-subtle); border-radius: var(--radius);
		border: 1px solid rgba(61, 90, 128, 0.12); letter-spacing: -0.02em;
	}
	.occ-info { flex: 1; }
	h1 { font-size: 1.5rem; font-weight: 700; color: var(--color-text); margin-bottom: 0.5rem; letter-spacing: -0.02em; line-height: 1.3; }
	.occ-desc { color: var(--color-text-secondary); font-size: 0.875rem; line-height: 1.6; margin-bottom: 0.625rem; }
	.header-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
	.header-tag {
		font-size: 0.6875rem; padding: 0.25rem 0.625rem; border-radius: 5px; font-weight: 600; border: none; font-family: var(--font);
		letter-spacing: 0.02em;
	}
	.header-tag.jz { background: var(--color-primary); color: white; }
	.header-tag.riasec { background: #805ad5; color: white; font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; letter-spacing: 1px; }
	.header-tag.source { background: var(--color-bg); color: var(--color-text-secondary); cursor: pointer; border: 1px solid var(--color-border); transition: all var(--transition); }
	.header-tag.source:hover { border-color: var(--color-border-hover); background: var(--color-border); }

	.layout { display: grid; grid-template-columns: 175px 1fr; gap: 1.75rem; }
	.sidebar { display: flex; flex-direction: column; gap: 0.125rem; position: sticky; top: 4.5rem; align-self: start; }

	.nav-item {
		display: block; padding: 0.45rem 0.75rem; background: none; border: none;
		border-left: 3px solid transparent; text-align: left; font-size: 0.8125rem;
		color: var(--color-text-secondary); cursor: pointer; border-radius: 0 var(--radius) var(--radius) 0; transition: all var(--transition);
		font-family: var(--font);
	}
	.nav-item:hover { background: var(--color-bg); color: var(--color-text); text-decoration: none; }
	.nav-item.active { border-left-color: var(--color-accent); background: var(--color-accent-subtle); color: var(--color-text); font-weight: 600; }
	.nav-divider { border: none; border-top: 1px solid var(--color-border); margin: 0.25rem 0; }
	.compare-link { color: var(--color-accent); font-size: 0.8rem; }

	.job-zone { margin-bottom: 1rem; padding: 0.5rem 0.75rem; background: var(--color-bg); border-radius: var(--radius); font-size: 0.9rem; }
	.alt-titles { margin-bottom: 1rem; font-size: 0.9rem; color: var(--color-text-secondary); line-height: 1.8; }

	.section-desc { color: var(--color-text-secondary); font-size: 0.8125rem; line-height: 1.55; margin-bottom: 1rem; }

	.mono { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; font-size: 0.8125rem; }
	.muted { color: var(--color-text-secondary); font-size: 0.85rem; }

	/* Source occupations */
	.source-list { display: flex; flex-direction: column; gap: 0.5rem; }
	.source-card {
		display: block; padding: 0.875rem; border: 1px solid var(--color-border);
		border-radius: var(--radius); color: var(--color-text); transition: all var(--transition);
		box-shadow: var(--shadow-xs);
	}
	.source-card:hover { border-color: var(--color-border-hover); box-shadow: var(--shadow); text-decoration: none; }
	.source-card-top { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem; }
	.source-code { color: var(--color-accent); flex: 0 0 auto; }
	.source-card .source-title { flex: 1; font-size: 0.9rem; }
	.source-weight { flex: 0 0 auto; font-size: 0.85rem; font-weight: 600; color: var(--color-text-secondary); }
	.source-bar-track { height: 6px; background: var(--color-border); border-radius: 3px; overflow: hidden; }
	.source-bar-fill { height: 100%; background: var(--color-accent); border-radius: 3px; transition: width 0.3s; }

	.task-items { display: flex; flex-direction: column; gap: 0.5rem; }
	.task-item { padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); }
	.task-item:last-child { border-bottom: none; }
	.task-content { display: flex; gap: 0.5rem; align-items: flex-start; }
	.task-text { flex: 1; font-size: 0.9rem; line-height: 1.5; overflow-wrap: break-word; }
	.task-badges { flex: 0 0 auto; display: flex; gap: 0.35rem; align-items: center; }
	.badge.supplemental { background: var(--color-text-secondary); }
	.badge.unclassified { background: #9ca3af; }
	.badge.emerging-new { background: var(--color-success); }
	.badge.emerging-revision { background: goldenrod; }

	.data-warning {
		padding: 0.75rem 1rem; margin-bottom: 1.25rem; border-radius: var(--radius);
		background: rgba(218, 165, 32, 0.08); border: 1px solid goldenrod;
		font-size: 0.875rem; color: var(--color-text); line-height: 1.5;
	}

	.emerging-card { border-left: 3px solid var(--color-success); }

	.dwa-list { display: flex; flex-direction: column; gap: 0.3rem; }
	.dwa-row { display: flex; align-items: center; gap: 0.75rem; }
	.dwa-label { flex: 0 0 300px; font-size: 0.8rem; text-align: right; color: var(--color-text-secondary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
	.dwa-bar-track { flex: 1; height: 10px; background: var(--color-border); border-radius: 4px; overflow: hidden; }
	.dwa-bar-fill { height: 100%; background: var(--color-accent); border-radius: 4px; transition: width 0.3s; }
	.dwa-val { flex: 0 0 35px; font-size: 0.8rem; color: var(--color-text-secondary); text-align: right; }

	.tech-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
	.tech-tag {
		padding: 0.3rem 0.75rem; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 20px; font-size: 0.8rem;
		transition: all var(--transition); box-shadow: var(--shadow-xs);
	}
	.tech-tag:hover { border-color: var(--color-border-hover); }

	/* Interest/RIASEC bars */
	.interest-bars { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 0.5rem; }
	.interest-row { display: flex; align-items: center; gap: 0.75rem; }
	.interest-code {
		flex: 0 0 28px; height: 28px; display: flex; align-items: center; justify-content: center;
		border-radius: 50%; background: var(--color-accent-bright); color: white; font-weight: 800; font-size: 0.85rem;
	}
	.interest-name { flex: 0 0 120px; font-size: 0.85rem; }
	.wv-name { flex: 0 0 160px; }
	.interest-bar-track { flex: 1; height: 18px; background: var(--color-bg); border: 1px solid rgba(0, 0, 0, 0.04); border-radius: 4px; overflow: hidden; }
	.interest-bar-fill { height: 100%; background: #805ad5; border-radius: 3px; transition: width 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94); }
	.wv-fill { background: var(--color-success); }
	.interest-val { flex: 0 0 35px; font-size: 0.85rem; color: var(--color-text-secondary); text-align: right; }
	.riasec-label { margin-top: 0.75rem; font-size: 0.9rem; }

	.edu-group-title { font-size: 0.95rem; color: var(--color-primary); margin: 1rem 0 0.25rem; font-weight: 600; }
	.edu-group-title:first-of-type { margin-top: 0; }
	.edu-list { display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.5rem; }
	.edu-row { display: flex; align-items: center; gap: 0.75rem; }
	.edu-label { flex: 0 0 220px; font-size: 0.85rem; text-align: right; color: var(--color-text-secondary); }

	.related-list { display: flex; flex-direction: column; }
	.related-item { display: flex; gap: 0.75rem; padding: 0.5rem 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); }
	.related-item:last-child { border-bottom: none; }
	.related-item:hover { color: var(--color-accent); text-decoration: none; }
	.related-code { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 600; color: var(--color-accent); flex: 0 0 50px; font-size: 0.8125rem; }

	.error { color: #e53e3e; text-align: center; padding: 1rem; }

	@media (max-width: 768px) {
		.layout { grid-template-columns: 1fr; }
		.sidebar { flex-direction: row; flex-wrap: wrap; position: static; }
		.nav-item { border-left: none; border-bottom: 2px solid transparent; border-radius: var(--radius); padding: 0.4rem 0.6rem; font-size: 0.8rem; }
		.nav-item.active { border-bottom-color: var(--color-accent); }
		.occ-header { flex-direction: column; }
		.interest-name { flex: 0 0 90px; }
		.edu-label { flex: 0 0 140px; font-size: 0.8rem; }
		.dwa-label { flex: 0 0 160px; font-size: 0.75rem; }
	}
</style>
