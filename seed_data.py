"""
Seed Data Script for Soosh Platform
Creates dummy data for categories, subcategories, users, mentors, and opportunities
"""

import asyncio
import random
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://vivekkumar@localhost:5432/soosh")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sample data
SUBCATEGORIES = {
    "Creativity & Arts": [
        ("Painting & Drawing", "painting-drawing", "Learn various painting and drawing techniques"),
        ("Music Production", "music-production", "Create and produce your own music"),
        ("Photography", "photography", "Master the art of photography"),
        ("Graphic Design", "graphic-design", "Design logos, posters, and digital art"),
        ("Writing & Storytelling", "writing", "Creative writing and storytelling skills"),
    ],
    "Education & Tutoring": [
        ("Mathematics", "mathematics", "Algebra, calculus, and advanced math"),
        ("Science & Physics", "science", "Biology, chemistry, and physics tutoring"),
        ("Language Learning", "languages", "Learn new languages with native speakers"),
        ("Test Prep", "test-prep", "SAT, ACT, GRE, and other exam preparation"),
        ("Computer Science", "computer-science", "Programming and CS fundamentals"),
    ],
    "Tech & Digital Innovation": [
        ("Web Development", "web-development", "Build modern websites and web apps"),
        ("Mobile App Development", "mobile-apps", "Create iOS and Android applications"),
        ("Data Science & AI", "data-science", "Machine learning and data analysis"),
        ("Cybersecurity", "cybersecurity", "Learn ethical hacking and security"),
        ("Cloud Computing", "cloud-computing", "AWS, Azure, and cloud infrastructure"),
    ],
    "Lifestyle & Wellness": [
        ("Fitness & Yoga", "fitness-yoga", "Personal training and yoga classes"),
        ("Mental Health", "mental-health", "Meditation, mindfulness, and therapy"),
        ("Nutrition & Diet", "nutrition", "Healthy eating and meal planning"),
        ("Personal Development", "personal-development", "Self-improvement and life coaching"),
        ("Cooking & Baking", "cooking", "Culinary arts and baking skills"),
    ],
    "Entrepreneurship & Side Hustles": [
        ("Freelancing", "freelancing", "Start your freelance career"),
        ("E-commerce", "ecommerce", "Build and grow online stores"),
        ("Digital Marketing", "digital-marketing", "SEO, social media, and content marketing"),
        ("Business Strategy", "business-strategy", "Startups and business planning"),
        ("Investment & Finance", "investment", "Stock market and personal finance"),
    ],
}

MENTOR_DATA = [
    ("Sarah", "Johnson", "sarah.j@example.com", ["Creativity & Arts"], ["UI/UX Design", "Product Design", "Figma"]),
    ("Michael", "Chen", "michael.c@example.com", ["Tech & Digital Innovation"], ["React", "Node.js", "Python"]),
    ("Emily", "Rodriguez", "emily.r@example.com", ["Tech & Digital Innovation"], ["Machine Learning", "Python", "TensorFlow"]),
    ("David", "Kim", "david.k@example.com", ["Entrepreneurship & Side Hustles"], ["Digital Marketing", "SEO", "Content Strategy"]),
    ("Lisa", "Thompson", "lisa.t@example.com", ["Lifestyle & Wellness"], ["Yoga", "Meditation", "Mindfulness"]),
    ("James", "Wilson", "james.w@example.com", ["Entrepreneurship & Side Hustles"], ["Investment", "Stock Trading", "Financial Planning"]),
    ("Maria", "Garcia", "maria.g@example.com", ["Creativity & Arts"], ["Piano", "Music Theory", "Voice Training"]),
    ("Robert", "Brown", "robert.b@example.com", ["Lifestyle & Wellness"], ["Personal Training", "Nutrition", "Weight Loss"]),
    ("Jennifer", "Lee", "jennifer.l@example.com", ["Education & Tutoring"], ["Spanish", "French", "ESL"]),
    ("Thomas", "Anderson", "thomas.a@example.com", ["Tech & Digital Innovation"], ["Ethical Hacking", "Network Security", "Penetration Testing"]),
]

OPPORTUNITIES = [
    # Creativity & Arts
    ("Beginner Painting Masterclass", "painting-drawing", "course", "BEGINNER",
     "Learn painting fundamentals from scratch. Perfect for absolute beginners wanting to explore their creative side.",
     8, 0, True, "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b", ["Creativity", "Art Fundamentals"]),

    ("Photography Portfolio Building", "photography", "mentorship", "INTERMEDIATE",
     "One-on-one mentorship to build a stunning photography portfolio. Get personalized feedback on your work.",
     12, 150.0, False, "https://images.unsplash.com/photo-1542038784456-1ea8e935640e", ["Photography", "Portfolio"]),

    ("Graphic Designer Position", "graphic-design", "job", "INTERMEDIATE",
     "Remote graphic designer needed for startup. Create social media graphics, logos, and marketing materials.",
     0, 3500.0, False, "https://images.unsplash.com/photo-1561070791-2526d30994b5", ["Adobe Creative Suite", "Design"]),

    # Education & Tutoring
    ("SAT Math Bootcamp", "test-prep", "course", "INTERMEDIATE",
     "Intensive 6-week SAT math preparation course. Score 750+ with proven strategies and practice tests.",
     24, 299.0, False, "https://images.unsplash.com/photo-1434030216411-0b793f4b4173", ["SAT", "Mathematics"]),

    ("Python Programming for Beginners", "computer-science", "course", "BEGINNER",
     "Learn Python from scratch. No coding experience required. Build real projects and understand programming fundamentals.",
     16, 0, True, "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5", ["Python", "Programming"]),

    # Tech & Digital Innovation
    ("Full Stack Web Development Bootcamp", "web-development", "course", "INTERMEDIATE",
     "12-week intensive bootcamp covering React, Node.js, MongoDB, and deployment. Build 5 real-world projects.",
     120, 999.0, False, "https://images.unsplash.com/photo-1498050108023-c5249f4df085", ["React", "Node.js", "MongoDB"]),

    ("Junior React Developer Position", "web-development", "job", "BEGINNER",
     "Remote junior developer role at fast-growing startup. Work with modern tech stack and experienced team.",
     0, 4500.0, False, "https://images.unsplash.com/photo-1555066931-4365d14bab8c", ["React", "JavaScript"]),

    ("AI & Machine Learning Workshop", "data-science", "workshop", "ADVANCED",
     "Weekend workshop on building ML models with TensorFlow. Hands-on experience with real datasets.",
     16, 499.0, False, "https://images.unsplash.com/photo-1555949963-aa79dcee981c", ["Machine Learning", "TensorFlow", "Python"]),

    # Lifestyle & Wellness
    ("Yoga for Beginners - 30 Day Challenge", "fitness-yoga", "course", "BEGINNER",
     "Transform your body and mind with daily yoga practice. Includes video lessons and personalized guidance.",
     20, 49.0, False, "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b", ["Yoga", "Fitness", "Wellness"]),

    ("Nutrition Coaching Program", "nutrition", "mentorship", "INTERMEDIATE",
     "12-week personalized nutrition coaching. Get custom meal plans and weekly check-ins with certified nutritionist.",
     24, 600.0, False, "https://images.unsplash.com/photo-1490645935967-10de6ba17061", ["Nutrition", "Health"]),

    # Entrepreneurship & Side Hustles
    ("Freelance Writing Success Course", "freelancing", "course", "BEGINNER",
     "Learn how to start and scale a freelance writing business. From finding clients to pricing your services.",
     12, 149.0, False, "https://images.unsplash.com/photo-1455390582262-044cdead277a", ["Freelancing", "Writing", "Business"]),

    ("E-commerce Store Launch Workshop", "ecommerce", "workshop", "BEGINNER",
     "3-day intensive workshop on launching your first online store. Covers Shopify, product selection, and marketing.",
     24, 299.0, False, "https://images.unsplash.com/photo-1472851294608-062f824d29cc", ["E-commerce", "Business", "Marketing"]),

    ("Digital Marketing Manager", "digital-marketing", "job", "ADVANCED",
     "Lead digital marketing efforts for growing SaaS company. Manage SEO, PPC, and content marketing strategies.",
     0, 6500.0, False, "https://images.unsplash.com/photo-1460925895917-afdab827c52f", ["SEO", "PPC", "Content Marketing"]),
]


async def seed_database():
    """Main function to seed the database with dummy data"""
    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Starting database seeding...")

            # Get category IDs
            print("\n📂 Fetching categories...")
            result = await session.execute(text("SELECT id, name FROM categories ORDER BY display_order"))
            categories = {row[1]: row[0] for row in result}
            print(f"✅ Found {len(categories)} categories")

            # Seed subcategories
            print("\n📂 Creating subcategories...")
            subcategory_map = {}
            for cat_name, subs in SUBCATEGORIES.items():
                if cat_name in categories:
                    cat_id = categories[cat_name]
                    for idx, (sub_name, sub_slug, sub_desc) in enumerate(subs):
                        sub_id = str(uuid4())
                        await session.execute(
                            text("""
                                INSERT INTO subcategories (id, category_id, name, slug, description, display_order)
                                VALUES (:id, :cat_id, :name, :slug, :desc, :order)
                                ON CONFLICT (slug) DO NOTHING
                            """),
                            {
                                "id": sub_id,
                                "cat_id": cat_id,
                                "name": sub_name,
                                "slug": sub_slug,
                                "desc": sub_desc,
                                "order": idx + 1
                            }
                        )
                        subcategory_map[sub_slug] = sub_id
            await session.commit()
            print(f"✅ Created {len(subcategory_map)} subcategories")

            # Seed mentor users
            print("\n👥 Creating mentor accounts...")
            mentor_ids = []
            for first, last, email, categories, skills in MENTOR_DATA:
                user_id = str(uuid4())
                password_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5nM3wfMPZn5Wy"  # "password123"

                # Create user
                await session.execute(
                    text("""
                        INSERT INTO users (id, email, password_hash, first_name, last_name, is_mentor, user_type, age_group, status)
                        VALUES (:id, :email, :password, :first, :last, true, 'EXPERIENCED', 'ADULT', 'ACTIVE')
                        ON CONFLICT (email) DO NOTHING
                    """),
                    {
                        "id": user_id,
                        "email": email,
                        "password": password_hash,
                        "first": first,
                        "last": last
                    }
                )

                # Create mentor profile with available hours (Mon-Fri 9am-5pm)
                available_hours = {
                    "monday": [{"start": "09:00", "end": "17:00"}],
                    "tuesday": [{"start": "09:00", "end": "17:00"}],
                    "wednesday": [{"start": "09:00", "end": "17:00"}],
                    "thursday": [{"start": "09:00", "end": "17:00"}],
                    "friday": [{"start": "09:00", "end": "17:00"}],
                }

                await session.execute(
                    text("""
                        INSERT INTO mentor_profiles (
                            id, user_id, expertise_categories, skills_offered,
                            available_hours, timezone, max_sessions_per_week,
                            average_rating, total_reviews, total_sessions_completed,
                            auto_accept_bookings
                        ) VALUES (
                            :id, :user_id, :categories::jsonb, :skills::jsonb,
                            :hours::jsonb, :timezone, :max_sessions,
                            :rating, :reviews, :sessions,
                            :auto_accept
                        )
                        ON CONFLICT (user_id) DO NOTHING
                    """),
                    {
                        "id": str(uuid4()),
                        "user_id": user_id,
                        "categories": json.dumps(categories),
                        "skills": json.dumps(skills),
                        "hours": json.dumps(available_hours),
                        "timezone": "America/New_York",
                        "max_sessions": random.randint(5, 15),
                        "rating": round(random.uniform(4.50, 5.00), 2),
                        "reviews": random.randint(10, 100),
                        "sessions": random.randint(20, 200),
                        "auto_accept": random.choice([True, False])
                    }
                )
                mentor_ids.append(user_id)
            await session.commit()
            print(f"✅ Created {len(mentor_ids)} mentor accounts")

            # Seed opportunities
            print("\n💼 Creating opportunities...")
            opp_count = 0
            for title, subcat_slug, opp_type, difficulty, desc, duration, price, is_free, thumbnail, skills in OPPORTUNITIES:
                if subcat_slug in subcategory_map:
                    creator_id = random.choice(mentor_ids)
                    subcat_id = subcategory_map[subcat_slug]

                    # Get category_id from subcategory
                    result = await session.execute(
                        text("SELECT category_id FROM subcategories WHERE id = :id"),
                        {"id": subcat_id}
                    )
                    cat_id = result.scalar()

                    opp_id = str(uuid4())
                    slug = title.lower().replace(" ", "-") + "-" + str(random.randint(1000, 9999))

                    start_date = datetime.now() + timedelta(days=random.randint(1, 30))
                    end_date = start_date + timedelta(days=duration * 7) if duration > 0 else None

                    await session.execute(
                        text("""
                            INSERT INTO opportunities (
                                id, creator_id, category_id, subcategory_id, title, slug,
                                description, opportunity_type, difficulty_level, duration_hours,
                                price, currency, is_free, thumbnail_url, skills_required,
                                is_active, is_published, views_count, enrollments_count,
                                avg_rating, start_date, end_date, is_remote
                            ) VALUES (
                                :id, :creator, :cat, :subcat, :title, :slug,
                                :desc, :type, :difficulty, :duration,
                                :price, 'USD', :is_free, :thumbnail, :skills,
                                true, true, :views, :enrollments,
                                :rating, :start_date, :end_date, true
                            )
                        """),
                        {
                            "id": opp_id,
                            "creator": creator_id,
                            "cat": cat_id,
                            "subcat": subcat_id,
                            "title": title,
                            "slug": slug,
                            "desc": desc,
                            "type": opp_type,
                            "difficulty": difficulty,
                            "duration": duration,
                            "price": price,
                            "is_free": is_free,
                            "thumbnail": thumbnail,
                            "skills": skills,
                            "views": random.randint(50, 1000),
                            "enrollments": random.randint(5, 200),
                            "rating": round(random.uniform(4.0, 5.0), 1),
                            "start_date": start_date,
                            "end_date": end_date
                        }
                    )
                    opp_count += 1
            await session.commit()
            print(f"✅ Created {opp_count} opportunities")

            # Create a test user for login
            print("\n🧪 Creating test user account...")
            test_user_id = str(uuid4())
            await session.execute(
                text("""
                    INSERT INTO users (
                        id, email, password_hash, first_name, last_name,
                        age, age_group, user_type, status
                    ) VALUES (
                        :id, 'test@soosh.com', :password, 'Test', 'User',
                        25, 'YOUNG_ADULT', 'BEGINNER', 'ACTIVE'
                    )
                    ON CONFLICT (email) DO NOTHING
                """),
                {
                    "id": test_user_id,
                    "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5nM3wfMPZn5Wy"  # "password123"
                }
            )
            await session.commit()
            print("✅ Test user created: test@soosh.com / password123")

            print("\n🎉 Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   - 5 main categories")
            print(f"   - {len(subcategory_map)} subcategories")
            print(f"   - {len(mentor_ids)} mentors")
            print(f"   - {opp_count} opportunities")
            print(f"   - 1 test user (test@soosh.com)")

        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            await session.rollback()
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("🌱 SOOSH DATABASE SEEDING SCRIPT")
    print("=" * 60)
    asyncio.run(seed_database())
