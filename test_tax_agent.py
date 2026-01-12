"""
Test script for the Tax Agent functionality
This script tests whether the tax knowledge base was loaded correctly
"""

import os
from pathlib import Path

def test_tax_knowledge_files():
    """Check if all tax knowledge files exist"""
    print("=" * 60)
    print("TESTING TAX KNOWLEDGE FILES")
    print("=" * 60)
    
    tax_dir = Path("tax_knowledge")
    
    if not tax_dir.exists():
        print("❌ ERROR: tax_knowledge directory not found!")
        return False
    
    expected_files = [
        "01_income_tax.txt",
        "02_vat.txt",
        "03_corporate_trade_tax.txt",
        "04_other_taxes.txt",
        "05_practical_examples_faq.txt"
    ]
    
    all_exist = True
    total_lines = 0
    total_size = 0
    
    for filename in expected_files:
        filepath = tax_dir / filename
        if filepath.exists():
            lines = len(filepath.read_text(encoding='utf-8').splitlines())
            size_kb = filepath.stat().st_size / 1024
            total_lines += lines
            total_size += size_kb
            print(f"✓ {filename}: {lines:,} lines ({size_kb:.1f} KB)")
        else:
            print(f"❌ {filename}: NOT FOUND")
            all_exist = False
    
    print(f"\n📊 TOTAL: {total_lines:,} lines across {len(expected_files)} files ({total_size:.1f} KB)")
    
    if all_exist:
        print("\n✅ All tax knowledge files are present!")
    else:
        print("\n❌ Some files are missing!")
    
    return all_exist

def test_main_py_modifications():
    """Check if main.py has the required modifications"""
    print("\n" + "=" * 60)
    print("TESTING MAIN.PY MODIFICATIONS")
    print("=" * 60)
    
    main_file = Path("main.py")
    
    if not main_file.exists():
        print("❌ ERROR: main.py not found!")
        return False
    
    content = main_file.read_text(encoding='utf-8')
    
    checks = {
        "Agent mode variable": "self.agent_mode = tk.StringVar",
        "Agent selector UI": "self.agent_selector = ttk.Combobox",
        "Tax collection init": "def init_tax_agent_collection",
        "Tax question processing": "def process_tax_agent_question",
        "Agent change handler": "def on_agent_change",
        "Agent routing in process_question": 'if agent == "tax_germany"',
        "Custom system prompt support": "custom_system_prompt=None"
    }
    
    all_present = True
    for check_name, check_string in checks.items():
        if check_string in content:
            print(f"✓ {check_name}")
        else:
            print(f"❌ {check_name}: NOT FOUND")
            all_present = False
    
    if all_present:
        print("\n✅ All required modifications are present in main.py!")
    else:
        print("\n❌ Some modifications are missing!")
    
    return all_present

def test_sample_questions():
    """Provide sample questions to test with the tax agent"""
    print("\n" + "=" * 60)
    print("SAMPLE QUESTIONS TO TEST")
    print("=" * 60)
    
    questions = [
        "What are the income tax brackets for 2025 in Germany?",
        "Explain the Kleinunternehmerregelung for VAT",
        "What is the corporate tax rate in Germany?",
        "How does trade tax (Gewerbesteuer) work?",
        "What are the church tax rates in different states?",
        "Explain the solidarity surcharge (Solidaritätszuschlag)",
        "What is the capital gains tax rate (Abgeltungsteuer)?",
        "How does the real estate transfer tax work?",
        "What are the inheritance tax exemptions?",
        "Calculate social security contributions for an employee"
    ]
    
    print("\nOnce the application starts, try these questions with the 'tax_germany' agent:\n")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    
    print("\n💡 TIP: Select 'tax_germany' from the agent dropdown before asking!")

if __name__ == "__main__":
    print("\n🇩🇪 TAX AGENT IMPLEMENTATION TEST\n")
    
    files_ok = test_tax_knowledge_files()
    code_ok = test_main_py_modifications()
    
    print("\n" + "=" * 60)
    print("OVERALL TEST RESULTS")
    print("=" * 60)
    
    if files_ok and code_ok:
        print("\n✅ ALL TESTS PASSED!")
        print("\nThe tax agent is ready to use!")
        print("\n📝 Next steps:")
        print("  1. Run: python main.py")
        print("  2. Select 'tax_germany' from the agent dropdown")
        print("  3. Ask any German tax question (no PDF upload needed)")
        print("  4. The agent will answer from the pre-loaded knowledge base")
        test_sample_questions()
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nPlease check the errors above and fix them before running the application.")
    
    print("\n" + "=" * 60)
