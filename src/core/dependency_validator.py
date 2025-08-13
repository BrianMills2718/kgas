"""
Fail-Fast Dependency Validator for KGAS System
NO MOCKS. NO SILENT FAILURES. NO GRACEFUL DEGRADATION.

This module validates all system dependencies and FAILS IMMEDIATELY 
with clear error messages when anything is missing or broken.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
import logging
import os
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)


class SystemMode(Enum):
    """Explicit system operation modes"""
    PRODUCTION = "production"       # All dependencies required
    DEVELOPMENT = "development"     # All dependencies required, clear errors
    TESTING = "testing"            # Explicit test mode with controlled dependencies
    OFFLINE = "offline"            # Explicitly no external dependencies (user choice)


class DependencyError(Exception):
    """Raised when required dependencies are missing"""
    def __init__(self, service_name: str, requirement: str, fix_command: str = None):
        self.service_name = service_name
        self.requirement = requirement
        self.fix_command = fix_command
        message = f"🔥 DEPENDENCY FAILURE: {service_name} - {requirement}"
        if fix_command:
            message += f"\n   FIX: {fix_command}"
        super().__init__(message)


class ServiceUnavailableError(Exception):
    """Raised when service is required but unavailable"""
    def __init__(self, service_name: str, reason: str, fix_steps: List[str] = None):
        self.service_name = service_name
        self.reason = reason
        self.fix_steps = fix_steps or []
        message = f"🔥 SERVICE UNAVAILABLE: {service_name} - {reason}"
        if fix_steps:
            message += "\n   FIX STEPS:"
            for i, step in enumerate(fix_steps, 1):
                message += f"\n     {i}. {step}"
        super().__init__(message)


class DependencyValidator:
    """Validates all system dependencies and fails fast on problems"""
    
    def __init__(self, mode: SystemMode = SystemMode.PRODUCTION):
        self.mode = mode
        self.logger = logging.getLogger(__name__)
        
        # Define required services based on mode
        if mode == SystemMode.OFFLINE:
            # Offline mode - only basic dependencies
            self.required_services = {
                'python_packages': self._check_python_packages,
                'sqlite': self._check_sqlite,
            }
        else:
            # All other modes require full dependencies
            self.required_services = {
                'python_packages': self._check_python_packages,
                'neo4j': self._check_neo4j,
                'sqlite': self._check_sqlite,
                'spacy_model': self._check_spacy_model
            }
    
    def validate_all_dependencies(self) -> None:
        """
        Validate all dependencies - FAIL FAST on any problems
        
        This method will raise SystemError if ANY dependency is missing or broken.
        NO SILENT FAILURES. NO FALLBACKS. NO MOCKS.
        """
        self.logger.info(f"🔍 Validating dependencies for {self.mode.value} mode...")
        
        failures = []
        successes = []
        
        for service_name, validator in self.required_services.items():
            try:
                validator()
                successes.append(service_name)
                self.logger.info(f"✅ {service_name}: OK")
            except (DependencyError, ServiceUnavailableError) as e:
                self.logger.error(f"❌ {service_name}: {e}")
                failures.append(e)
            except Exception as e:
                # Catch unexpected errors and wrap them
                failure = ServiceUnavailableError(
                    service_name,
                    f"Unexpected validation error: {str(e)}",
                    ["Check logs for details", "Report this as a bug"]
                )
                self.logger.error(f"❌ {service_name}: {failure}")
                failures.append(failure)
        
        if failures:
            self._handle_dependency_failures(failures, successes)
        else:
            self.logger.info(f"🎉 All dependencies validated successfully for {self.mode.value} mode")
    
    def _check_python_packages(self) -> None:
        """Check required Python packages"""
        required_packages = {
            # Core packages
            'neo4j': 'Neo4j Python driver - pip install neo4j',
            'spacy': 'spaCy NLP library - pip install spacy',
            'pandas': 'Data manipulation - pip install pandas',
            'numpy': 'Numerical computing - pip install numpy',
            'psutil': 'System monitoring - pip install psutil',
            
            # Optional but recommended
            'pypdf': 'PDF processing - pip install pypdf',
            'networkx': 'Graph algorithms - pip install networkx',
            'scipy': 'Scientific computing - pip install scipy',
        }
        
        missing_packages = []
        
        for package, description in required_packages.items():
            try:
                __import__(package)
            except ImportError:
                # Only fail on core packages in non-offline mode
                if package in ['neo4j', 'spacy', 'pandas', 'numpy', 'psutil'] and self.mode != SystemMode.OFFLINE:
                    missing_packages.append((package, description))
                elif package in ['pypdf', 'networkx', 'scipy']:
                    # Warn about optional packages but don't fail
                    self.logger.warning(f"⚠️ Optional package missing: {package}")
        
        if missing_packages:
            error_msg = "Required Python packages missing:\n"
            for package, description in missing_packages:
                error_msg += f"  - {package}: {description}\n"
            
            raise DependencyError(
                "python_packages",
                error_msg.strip(),
                f"pip install {' '.join(pkg for pkg, _ in missing_packages)}"
            )
    
    def _check_neo4j(self) -> None:
        """Check Neo4j availability - FAIL if not available"""
        if self.mode == SystemMode.OFFLINE:
            # Don't check Neo4j in offline mode
            return
        
        try:
            from neo4j import GraphDatabase
            
            # Get connection details
            uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
            username = os.environ.get("NEO4J_USERNAME", "neo4j")
            password = os.environ.get("NEO4J_PASSWORD", "")  # Empty password OK for minimal security
            
            # Attempt connection
            driver = GraphDatabase.driver(uri, auth=(username, password))
            
            # Test connection with a simple query
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            # Test write capability
            with driver.session() as session:
                session.run("CREATE (t:Test {id: 'dependency_check'}) DELETE t")
            
            driver.close()
            
        except ImportError:
            # This should have been caught by package check
            raise DependencyError(
                "neo4j", 
                "Neo4j Python driver not installed",
                "pip install neo4j"
            )
        except Exception as e:
            error_msg = f"Cannot connect to Neo4j at {uri}: {str(e)}"
            
            # Provide specific fix steps based on error type
            fix_steps = [
                "Check if Neo4j is running:",
                "  docker ps | grep neo4j",
                "",
                "Start Neo4j if not running:",
                "  docker run -d -p 7474:7474 -p 7687:7687 --name neo4j neo4j:latest",
                "  OR: docker-compose up -d neo4j",
                "",
                "Check connection details:",
                f"  NEO4J_URI={uri}",
                f"  NEO4J_USERNAME={username}",
                f"  NEO4J_PASSWORD={password}",
                "",
                "Test connection manually:",
                f"  docker exec -it neo4j cypher-shell -u {username} -p {password}",
                "",
                "Alternative: Use offline mode if Neo4j not needed:",
                "  export KGAS_MODE=offline"
            ]
            
            raise ServiceUnavailableError("neo4j", error_msg, fix_steps)
    
    def _check_sqlite(self) -> None:
        """Check SQLite availability and permissions"""
        try:
            # Check if sqlite3 module is available
            import sqlite3
            
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)
            
            # Test database creation and operations
            test_db_path = data_dir / "dependency_test.db"
            
            # Test write permissions
            conn = sqlite3.connect(str(test_db_path))
            cursor = conn.cursor()
            
            # Test table creation
            cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
            
            # Test insert
            cursor.execute("INSERT INTO test (id) VALUES (1)")
            
            # Test select
            cursor.execute("SELECT COUNT(*) FROM test")
            count = cursor.fetchone()[0]
            
            # Test delete
            cursor.execute("DELETE FROM test")
            
            # Test drop
            cursor.execute("DROP TABLE test")
            
            conn.commit()
            conn.close()
            
            # Clean up test database
            if test_db_path.exists():
                test_db_path.unlink()
            
        except ImportError:
            raise DependencyError(
                "sqlite",
                "SQLite3 module not available",
                "SQLite3 should be included with Python - check your Python installation"
            )
        except PermissionError as e:
            raise ServiceUnavailableError(
                "sqlite",
                f"Permission denied accessing data directory: {e}",
                [
                    "Check directory permissions: ls -la data/",
                    "Fix permissions: chmod 755 data/",
                    "Check disk space: df -h",
                    "Run as different user if needed"
                ]
            )
        except Exception as e:
            raise ServiceUnavailableError(
                "sqlite",
                f"SQLite test operations failed: {e}",
                [
                    "Check disk space: df -h",
                    "Check write permissions to data/ directory",
                    "Verify SQLite installation: python -c 'import sqlite3; print(sqlite3.version)'"
                ]
            )
    
    def _check_spacy_model(self) -> None:
        """Check spaCy model availability"""
        if self.mode == SystemMode.OFFLINE:
            # Don't require spaCy model in offline mode
            return
        
        try:
            import spacy
            
            # Try to load the required model
            model_name = "en_core_web_sm"
            nlp = spacy.load(model_name)
            
            # Test basic functionality
            doc = nlp("Test sentence for dependency validation.")
            
            # Verify it has the required components
            if not doc.ents and not doc[0].pos_:
                raise ServiceUnavailableError(
                    "spacy_model",
                    f"spaCy model {model_name} loaded but not functioning correctly",
                    [
                        f"Reinstall model: python -m spacy download {model_name}",
                        "Check model integrity: python -c \"import spacy; nlp = spacy.load('en_core_web_sm'); print(nlp.pipe_names)\""
                    ]
                )
            
        except ImportError:
            # This should have been caught by package check
            raise DependencyError(
                "spacy",
                "spaCy not installed",
                "pip install spacy"
            )
        except OSError as e:
            if "Can't find model" in str(e):
                raise ServiceUnavailableError(
                    "spacy_model",
                    f"spaCy model 'en_core_web_sm' not found",
                    [
                        "Download model: python -m spacy download en_core_web_sm",
                        "Verify installation: python -c \"import spacy; spacy.load('en_core_web_sm')\"",
                        "List available models: python -m spacy info"
                    ]
                )
            else:
                raise ServiceUnavailableError(
                    "spacy_model",
                    f"spaCy model loading error: {e}",
                    [
                        "Reinstall spaCy: pip uninstall spacy && pip install spacy",
                        "Redownload model: python -m spacy download en_core_web_sm --force"
                    ]
                )
        except Exception as e:
            raise ServiceUnavailableError(
                "spacy_model",
                f"spaCy model test failed: {e}",
                [
                    "Test model manually: python -c \"import spacy; nlp = spacy.load('en_core_web_sm'); print(nlp('test'))\"",
                    "Reinstall if needed: python -m spacy download en_core_web_sm --force"
                ]
            )
    
    def _handle_dependency_failures(self, failures: List[Exception], successes: List[str]) -> None:
        """Handle dependency failures - ALWAYS FAIL, NEVER CONTINUE"""
        
        # Build comprehensive error message
        separator = "=" * 80
        error_msg = f"\n{separator}\n"
        error_msg += f"🔥 DEPENDENCY VALIDATION FAILED ({len(failures)} issues)\n"
        error_msg += f"{separator}\n\n"
        
        # Show what succeeded
        if successes:
            error_msg += f"✅ WORKING DEPENDENCIES ({len(successes)}):\n"
            for service in successes:
                error_msg += f"   • {service}\n"
            error_msg += "\n"
        
        # Show what failed
        error_msg += f"❌ FAILED DEPENDENCIES ({len(failures)}):\n\n"
        for i, failure in enumerate(failures, 1):
            error_msg += f"{i}. {failure}\n\n"
        
        # Add mode-specific guidance
        error_msg += f"SYSTEM MODE: {self.mode.value}\n\n"
        
        if self.mode == SystemMode.PRODUCTION:
            error_msg += "🏭 PRODUCTION MODE: All dependencies must be working.\n"
            error_msg += "   Fix all issues above before starting the system.\n\n"
        elif self.mode == SystemMode.DEVELOPMENT:
            error_msg += "🛠️  DEVELOPMENT MODE: Fix dependencies to continue.\n"
            error_msg += "   Alternative: export KGAS_MODE=offline (limited functionality)\n\n"
        elif self.mode == SystemMode.TESTING:
            error_msg += "🧪 TESTING MODE: Use test doubles or fix dependencies.\n"
            error_msg += "   Make sure test environment is properly configured.\n\n"
        
        # Quick fix summary
        error_msg += "QUICK FIXES:\n"
        error_msg += "  • Install packages: pip install neo4j spacy pandas numpy psutil\n"
        error_msg += "  • Download spaCy model: python -m spacy download en_core_web_sm\n"
        error_msg += "  • Start Neo4j: docker run -d -p 7474:7474 -p 7687:7687 neo4j:latest\n"
        error_msg += "  • Use offline mode: export KGAS_MODE=offline\n\n"
        
        error_msg += separator
        
        # FAIL FAST - raise SystemError to stop everything
        raise SystemError(error_msg)


def detect_system_mode() -> SystemMode:
    """Detect system mode from environment variables"""
    mode_str = os.environ.get('KGAS_MODE', 'production').lower()
    
    mode_mapping = {
        'production': SystemMode.PRODUCTION,
        'prod': SystemMode.PRODUCTION,
        'development': SystemMode.DEVELOPMENT,
        'dev': SystemMode.DEVELOPMENT,
        'testing': SystemMode.TESTING,
        'test': SystemMode.TESTING,
        'offline': SystemMode.OFFLINE
    }
    
    return mode_mapping.get(mode_str, SystemMode.PRODUCTION)


def validate_system_dependencies(mode: SystemMode = None) -> None:
    """
    Validate all system dependencies for the given mode.
    
    This is the main entry point for dependency validation.
    Call this at system startup to ensure all dependencies are available.
    
    Args:
        mode: System mode to validate for. If None, detects from environment.
        
    Raises:
        SystemError: If any dependencies are missing or broken
        
    Example:
        validate_system_dependencies()  # Uses environment KGAS_MODE
        validate_system_dependencies(SystemMode.DEVELOPMENT)  # Explicit mode
    """
    if mode is None:
        mode = detect_system_mode()
    
    validator = DependencyValidator(mode)
    validator.validate_all_dependencies()