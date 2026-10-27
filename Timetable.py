import math
import random

# =============================================================
# DATA SETUP & AUTOMATIC SECTION PARTITIONING (MAX 40 STUDENTS)
# =============================================================

MAX_SECTION_CAPACITY = 40

# Raw course enrollment numbers
course_enrollments = {
    "AI": 75,                 # Splits into 2 sections (38, 37)
    "Database": 40,           # Exactly 1 section (40)
    "Data Structure": 85,     # Splits into 3 sections (29, 28, 28)
    "Computer Networks": 35,  # Exactly 1 section (35)
    "Mathematics": 90,        # Splits into 3 sections (30, 30, 30)
    "Operating System": 45    # Splits into 2 sections (23, 22)
}

course_teachers = {
    "AI": "Teacher A",
    "Database": "Teacher B",
    "Data Structure": "Teacher C",
    "Computer Networks": "Teacher A",
    "Mathematics": "Teacher E",
    "Operating System": "Teacher F"
}

# Room capacities
room_capacities = {
    "Room 101": 45,
    "Room 102": 40,
    "Room 103": 35
}

teacher_off_days = {
    "Teacher A": "Sunday",
    "Teacher B": "Thursday"
}

days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
times = ["9-10", "10-11", "11-12", "12-1"]
rooms = list(room_capacities.keys())

# Generate sections dynamically ensuring max 40 students per section
schedulable_units = []  # List of dicts representing each section to schedule

for course, total_students in course_enrollments.items():
    num_sections = math.ceil(total_students / MAX_SECTION_CAPACITY)
    base_students = total_students // num_sections
    remainder = total_students % num_sections

    for i in range(num_sections):
        # Distribute students evenly across sections
        sec_size = base_students + (1 if i < remainder else 0)
        sec_name = f"{course} - Sec {chr(65 + i)}"
        
        schedulable_units.append({
            "course": course,
            "section_name": sec_name,
            "students": sec_size,
            "teacher": course_teachers[course]
        })


# =============================================================
# GENETIC ALGORITHM FOR TIMETABLE SCHEDULING
# =============================================================

def create_gene(unit_index):
    return {
        "unit_idx": unit_index,
        "day": random.choice(days),
        "time": random.choice(times),
        "room": random.choice(rooms)
    }

def create_chromosome():
    return [create_gene(i) for i in range(len(schedulable_units))]

def create_population(size):
    return [create_chromosome() for _ in range(size)]

def fitness(chromosome):
    penalty = 0

    for i in range(len(chromosome)):
        g1 = chromosome[i]
        u1 = schedulable_units[g1["unit_idx"]]

        # 1. Enforce section cap limit
        if u1["students"] > MAX_SECTION_CAPACITY:
            penalty += 100

        # 2. Room capacity check
        if u1["students"] > room_capacities[g1["room"]]:
            penalty += 100

        # 3. Teacher off-day check
        if teacher_off_days.get(u1["teacher"]) == g1["day"]:
            penalty += 100

        # 4. Overlap checks
        for j in range(i + 1, len(chromosome)):
            g2 = chromosome[j]
            u2 = schedulable_units[g2["unit_idx"]]

            if g1["day"] == g2["day"] and g1["time"] == g2["time"]:
                # Same room double-booked
                if g1["room"] == g2["room"]:
                    penalty += 100
                # Same teacher double-booked
                if u1["teacher"] == u2["teacher"]:
                    penalty += 100
                # Same section double-booked
                if u1["section_name"] == u2["section_name"]:
                    penalty += 100

    # Soft constraint: prefer earlier timeslots over 12-1
    for g in chromosome:
        if g["time"] == "12-1":
            penalty += 1

    return 1 / (1 + penalty)

def selection(population):
    population.sort(key=fitness, reverse=True)
    return population[:4]

def crossover(p1, p2):
    pt = random.randint(1, len(p1) - 1)
    return p1[:pt] + p2[pt:], p2[:pt] + p1[pt:]

def mutation(chromosome, rate=0.15):
    mutated = [gene.copy() for gene in chromosome]
    for i in range(len(mutated)):
        if random.random() < rate:
            mutated[i] = create_gene(mutated[i]["unit_idx"])
    return mutated


# =============================================================
# EXECUTION & DISPLAY
# =============================================================

population_size = 50
generations = 250
population = create_population(population_size)

for gen in range(generations):
    best = max(population, key=fitness)
    current_fitness = fitness(best)

    if current_fitness == 1.0:
        print(f"Optimal timetable resolved at Generation {gen + 1}!\n")
        break

    parents = selection(population)
    new_population = parents[:2]

    while len(new_population) < population_size:
        p1, p2 = random.choice(parents), random.choice(parents)
        c1, c2 = crossover(p1, p2)
        new_population.extend([mutation(c1), mutation(c2)])

    population = new_population[:population_size]

best_schedule = max(population, key=fitness)

print("=" * 95)
print(f"{'Section Name':<25} | {'Teacher':<12} | {'Students':<10} | {'Day':<10} | {'Time':<8} | {'Room (Cap)'}")
print("=" * 95)

for gene in sorted(best_schedule, key=lambda x: (x["day"], x["time"])):
    u = schedulable_units[gene["unit_idx"]]
    room_info = f"{gene['room']} ({room_capacities[gene['room']]})"
    print(f"{u['section_name']:<25} | {u['teacher']:<12} | {u['students']:<10} | {gene['day']:<10} | {gene['time']:<8} | {room_info}")

print("-" * 95)
print(f"Final Schedule Fitness: {fitness(best_schedule):.4f}")