const API_BASE = 'http://localhost:8000/api';

async function fetchJson<T>(path: string): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`);
	if (!res.ok) throw new Error(`API error: ${res.status}`);
	return res.json();
}

export interface Occupation {
	uk_soc_2020: number;
	title: string;
}

export interface OccupationDetail {
	uk_soc_2020: number;
	title: string;
	description: string;
	abilities: RatedElement[];
	skills: RatedElement[];
	knowledge: RatedElement[];
	work_activities: RatedElement[];
	work_context: RatedElement[];
	work_styles: RatedElement[];
	interests: RatedElement[];
	work_values: RatedElement[];
	tasks: Task[];
	technology_skills: TechSkill[];
	education: EducationEntry[];
	job_zone: number;
	related_occupations: RelatedOccupation[];
	alternate_titles: string[];
	source_occupations: SourceOccupation[];
}

export interface RatedElement {
	element_id: string;
	element_name: string;
	value_IM?: number;
	value_LV?: number;
}

export interface Task {
	task: string;
	task_type: string;
	relevance: number;
}

export interface TechSkill {
	name: string;
	weight: number;
}

export interface EducationEntry {
	Element_Name: string;
	Scale_ID: string;
	Category: number;
	'Data Value': number;
}

export interface RelatedOccupation {
	related_uk_soc: number;
	related_uk_title: string;
	link_count: number;
}

export interface SourceOccupation {
	onet_soc: string;
	onet_title: string;
	weight: number;
}

export interface MajorGroup {
	code: number;
	title: string;
	occupation_count: number;
}

export async function searchOccupations(q: string, limit = 50, offset = 0) {
	return fetchJson<{ total: number; occupations: Occupation[] }>(
		`/occupations?q=${encodeURIComponent(q)}&limit=${limit}&offset=${offset}`
	);
}

export async function listOccupations(majorGroup?: number, limit = 50, offset = 0) {
	let url = `/occupations?limit=${limit}&offset=${offset}`;
	if (majorGroup !== undefined) url += `&major_group=${majorGroup}`;
	return fetchJson<{ total: number; occupations: Occupation[] }>(url);
}

export async function getOccupation(socCode: number) {
	return fetchJson<OccupationDetail>(`/occupations/${socCode}`);
}

export async function getMajorGroups() {
	return fetchJson<{ major_groups: MajorGroup[] }>('/browse/major-groups');
}

export async function getStats() {
	return fetchJson<{
		total_occupations: number;
		soc_version: string;
		source: string;
		data_categories: string[];
	}>('/stats');
}
